import ctypes
import datetime
import os
import sys
from typing import Union

import xlsxwriter as xlsx
from pandas import read_excel

from logger import setup_logger
from pywinbot import Address, MemoryReader
from strings import get_strings
import traceback

INVENTORY_BASE_ADDRESS = Address("007BA638")
PLAYER_BASE_ADDRESS = Address("00D511D8")
CREDENTIALS_BASE_ADDRESS = Address("007BA650")
IS_ADMIN = ctypes.windll.shell32.IsUserAnAdmin() != 0

logger = setup_logger()


def show_exception_and_exit(exc_type, exc_value, tb):
    logger.error(traceback.format_exception(exc_type, exc_value, tb))
    sys.exit(-1)

sys.excepthook = show_exception_and_exit


def get_character_name() -> str:
    length_pointer = mr.get_final_pointer(PLAYER_BASE_ADDRESS,
                                          ["240", "84", "8", "-4"])
    name_pointer = mr.get_final_pointer(PLAYER_BASE_ADDRESS,
                                        ["240", "84", "8", "0"])

    length: int = mr.read(length_pointer, "b", 1)

    return mr.read(name_pointer, "str", length)


def get_account_id() -> str:
    length_pointer = mr.get_final_pointer(CREDENTIALS_BASE_ADDRESS,
                                          ["34"])
    id_pointer = mr.get_final_pointer(CREDENTIALS_BASE_ADDRESS,
                                      ["24"])

    length: int = mr.read(length_pointer, "b", 1)

    return mr.read(id_pointer, "str", length)


class InventarSlot:
    def __init__(self, slot_id: int):
        self.slot_id: int = slot_id

        # Calculate offset
        offset_1 = Address("20") + Address("4") * slot_id

        # Calculate pointers
        self.quantity_pointer = mr.get_final_pointer(INVENTORY_BASE_ADDRESS,
                                                     [offset_1.address_string,
                                                      "56"])

        self.table_pointer = mr.get_final_pointer(INVENTORY_BASE_ADDRESS,
                                                  [offset_1.address_string,
                                                   "5C"])

        self.row_pointer = mr.get_final_pointer(INVENTORY_BASE_ADDRESS,
                                                [offset_1.address_string,
                                                 "60"])

    def __repr__(self) -> str:
        if not self.is_empty:
            return f"<InventarSlot{self.slot_id} Quantity={self.quantity} Code=<i|{self.table},{self.row}|> >"
        else:
            return f"<InventarSlot{self.slot_id} Empty>"

    @property
    def quantity(self) -> Union[int, None]:
        return mr.read(self.quantity_pointer, "h", 2)

    @property
    def table(self) -> Union[int, None]:
        return mr.read(self.table_pointer, "h", 2)

    @property
    def row(self) -> Union[int, None]:
        return mr.read(self.row_pointer, "h", 2)

    @property
    def is_empty(self) -> bool:
        return True if self.quantity is None else False


if __name__ == "__main__":
    if not IS_ADMIN:
        logger.warning("Script has to run as Administrator.")
        sys.exit(-1)

    mr = MemoryReader(process_name="FlorensiaEN.bin",
                      window_class="Florensia")

    logger.info("Starting Inventory Database Tool...")
    character_name = get_character_name()
    account_id = get_account_id()
    logger.info(f"Creating database for {account_id} - {character_name}")

    logger.info("Getting item strings")
    mapper = get_strings()
    logger.info("Got 'em!")

    slots = [InventarSlot(i+1) for i in range(0, 120)]

    headers = ["Account ID", "Character", "Type",
               "Name", "Quantity", "Slot", "Updated"]
    rows = []

    logger.info("Getting inventory slots")
    for slot in slots:
        if not slot.is_empty:
            item: dict = mapper[str(slot.table)][str(slot.row)]
            rows.append([
                account_id,
                character_name,
                item["type"],
                item["name"],
                slot.quantity,
                slot.slot_id,
                str(datetime.datetime.now())
            ])
    logger.info("Got 'em!")

    # Check if file exists -> add data from file to rows list
    if os.path.exists("InventoryDatabase.xlsx"):
        logger.info("Found an existing file.")
        data = read_excel("InventoryDatabase.xlsx").to_dict("split")["data"]
        for row in data:
            # just add data that is not from this char and account
            # because this is already present in rows list
            if not (row[0] == account_id and row[1] == character_name):
                rows.append(row)

    logger.info("Creating excel file")
    wb = xlsx.Workbook(filename="InventoryDatabase.xlsx")
    bold = wb.add_format({"bold": True})
    sheet = wb.add_worksheet()

    # Write data
    sheet.write_row(0, 0, headers, bold)
    for index, row in enumerate(rows):
        sheet.write_row(index+1, 0, row)

    sheet.autofilter(0, 0, len(rows), len(headers)-2)

    wb.close()
    logger.info("Finished\n")
