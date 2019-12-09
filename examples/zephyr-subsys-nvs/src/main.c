#include <zephyr.h>
#include <power/reboot.h>
#include <device.h>
#include <string.h>
#include <drivers/flash.h>
#include <fs/nvs.h>

static struct nvs_fs fs;

/* 1000 msec = 1 sec */
#define SLEEP_TIME      100
/* maximum reboot counts, make high enough to trigger sector change (buffer */
/* rotation). */
#define MAX_REBOOT 400

#define ADDRESS_ID 1
#define KEY_ID 2
#define RBT_CNT_ID 3
#define STRING_ID 4
#define LONG_ID 5


void main(void)
{
	int rc = 0, cnt = 0, cnt_his = 0;
	char buf[16];
	u8_t key[8], longarray[128];
	u32_t reboot_counter = 0U, reboot_counter_his;
	struct flash_pages_info info;

	/* define the nvs file system by settings with:
	 *	sector_size equal to the pagesize,
	 *	3 sectors
	 *	starting at DT_FLASH_AREA_STORAGE_OFFSET
	 */
	fs.offset = DT_FLASH_AREA_STORAGE_OFFSET;
	rc = flash_get_page_info_by_offs(device_get_binding(DT_FLASH_DEV_NAME),
					 fs.offset, &info);
	if (rc) {
		printk("Unable to get page info");
	}
	fs.sector_size = info.size;
	fs.sector_count = 3U;

	rc = nvs_init(&fs, DT_FLASH_DEV_NAME);
	if (rc) {
		printk("Flash Init failed\n");
	}

	/* ADDRESS_ID is used to store an address, lets see if we can
	 * read it from flash, since we don't know the size read the
	 * maximum possible
	 */
	rc = nvs_read(&fs, ADDRESS_ID, &buf, sizeof(buf));
	if (rc > 0) { /* item was found, show it */
		printk("Id: %d, Address: %s\n", ADDRESS_ID, buf);
	} else   {/* item was not found, add it */
		strcpy(buf, "192.168.1.1");
		printk("No address found, adding %s at id %d\n", buf,
		       ADDRESS_ID);
		nvs_write(&fs, ADDRESS_ID, &buf, strlen(buf)+1);
	}
	/* KEY_ID is used to store a key, lets see if we can read it from flash
	 */
	rc = nvs_read(&fs, KEY_ID, &key, sizeof(key));
	if (rc > 0) { /* item was found, show it */
		printk("Id: %d, Key: ", KEY_ID);
		for (int n = 0; n < 8; n++) {
			printk("%x ", key[n]);
		}
		printk("\n");
	} else   {/* item was not found, add it */
		printk("No key found, adding it at id %d\n", KEY_ID);
		key[0] = 0xFF;
		key[1] = 0xFE;
		key[2] = 0xFD;
		key[3] = 0xFC;
		key[4] = 0xFB;
		key[5] = 0xFA;
		key[6] = 0xF9;
		key[7] = 0xF8;
		nvs_write(&fs, KEY_ID, &key, sizeof(key));
	}
	/* RBT_CNT_ID is used to store the reboot counter, lets see
	 * if we can read it from flash
	 */
	rc = nvs_read(&fs, RBT_CNT_ID, &reboot_counter, sizeof(reboot_counter));
	if (rc > 0) { /* item was found, show it */
		printk("Id: %d, Reboot_counter: %d\n",
			RBT_CNT_ID, reboot_counter);
	} else   {/* item was not found, add it */
		printk("No Reboot counter found, adding it at id %d\n",
		       RBT_CNT_ID);
		nvs_write(&fs, RBT_CNT_ID, &reboot_counter,
			  sizeof(reboot_counter));
	}
	/* STRING_ID is used to store data that will be deleted,lets see
	 * if we can read it from flash, since we don't know the size read the
	 * maximum possible
	 */
	rc = nvs_read(&fs, STRING_ID, &buf, sizeof(buf));
	if (rc > 0) {
		/* item was found, show it */
		printk("Id: %d, Data: %s\n",
			STRING_ID, buf);
		/* remove the item if reboot_counter = 10 */
		if (reboot_counter == 10U) {
			nvs_delete(&fs, STRING_ID);
		}
	} else   {
		/* entry was not found, add it if reboot_counter = 0*/
		if (reboot_counter == 0U) {
			printk("Id: %d not found, adding it\n",
			STRING_ID);
			strcpy(buf, "DATA");
			nvs_write(&fs, STRING_ID, &buf, strlen(buf) + 1);
		}
	}

	/* LONG_ID is used to store a larger dataset ,lets see if we can read
	 * it from flash
	 */
	rc = nvs_read(&fs, LONG_ID, &longarray, sizeof(longarray));
	if (rc > 0) {
		/* item was found, show it */
		printk("Id: %d, Longarray: ", LONG_ID);
		for (int n = 0; n < sizeof(longarray); n++) {
			printk("%x ", longarray[n]);
		}
		printk("\n");
	} else   {
		/* entry was not found, add it if reboot_counter = 0*/
		if (reboot_counter == 0U) {
			printk("Longarray not found, adding it as id %d\n",
			       LONG_ID);
			for (int n = 0; n < sizeof(longarray); n++) {
				longarray[n] = n;
			}
			nvs_write(&fs, LONG_ID, &longarray, sizeof(longarray));
		}
	}

	cnt = 5;
	while (1) {
		k_sleep(SLEEP_TIME);
		if (reboot_counter < MAX_REBOOT) {
			if (cnt == 5) {
				/* print some history information about
				 * the reboot counter
				 * Check the counter history in flash
				 */
				printk("Reboot counter history: ");
				while (1) {
					rc = nvs_read_hist(
						&fs, RBT_CNT_ID,
						&reboot_counter_his,
						sizeof(reboot_counter_his),
						cnt_his);
					if (rc < 0) {
						break;
					}
					printk("...%d", reboot_counter_his);
					cnt_his++;
				}
				if (cnt_his == 0) {
					printk("\n Error, no Reboot counter");
				} else {
					printk("\nOldest reboot counter: %d",
					       reboot_counter_his);
				}
				printk("\nRebooting in ");
			}
			printk("...%d", cnt);
			cnt--;
			if (cnt == 0) {
				printk("\n");
				reboot_counter++;
				nvs_write(
					&fs, RBT_CNT_ID, &reboot_counter,
					sizeof(reboot_counter));
				if (reboot_counter == MAX_REBOOT) {
					printk("Doing last reboot...\n");
				}
				sys_reboot(0);
			}
		} else {
			printk("Reboot counter reached max value.\n");
			printk("Reset to 0 and exit test.\n");
			reboot_counter = 0U;
			nvs_write(&fs, RBT_CNT_ID, &reboot_counter,
			  sizeof(reboot_counter));
			break;
		}
	}
}
