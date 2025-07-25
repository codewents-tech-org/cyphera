# asset_table_utils.py

from PyQt5.QtWidgets import QMessageBox

def store_selected_entry(self, item):
    self.refrash_existing_entries()
    self.previous_text = item.text()

def find_duplicates(self, changed_item):
    # counter = Counter(existing_records)
    changed_text = changed_item.text().strip()
    self.refrash_existing_entries()
    print(self.previous_text)
    # if self.previous_text: self.existing_entries.discard(self.previous_text)
    existing_lower = {entry.lower() for entry in self.existing_entries}
    if changed_text == '': 
        QMessageBox.warning(None, "Name Error", f"Name Should not be empty.")
        count = 0
        new_text = 'copy'
        # Loop to find the first available copy name
        while new_text.lower() in existing_lower:
            count += 1
            new_text = f"{new_text} {count if count>0 else ''}"
        if self.previous_text: changed_item.setText(self.previous_text)
        else: changed_item.setText(new_text.strip())
        self.existing_entries.add(new_text.strip())
    elif changed_text.lower() in existing_lower : 
        QMessageBox.warning(None, "Name Error", f"'{changed_text}' is already available. Please change the name.")
        # Find the count of duplicates (append "(copy X)" to make unique)
        count = 0
        new_text = changed_text
        # Loop to find the first available copy name
        while new_text.strip().lower() in existing_lower:
            new_text = f"{changed_text} copy{count if count>0 else ''}"
            count += 1
        changed_item.setText(new_text.strip())
        self.existing_entries.add(new_text.strip())
    else: 
        self.existing_entries.add(changed_text.strip())
    self.refrash_existing_entries()

def refrash_existing_entries(self):
    existing_lower = {entry.lower() for entry in self.existing_entries}
    available_entry = []
    row_count = self.table.rowCount()
    for row in range(row_count):
        name_item = self.table.item(row, 2)
        if name_item and name_item.text().lower() not in available_entry: available_entry.append(name_item.text().lower())
    remove_entrys = []
    for entry in existing_lower: 
        if entry not in available_entry: remove_entrys.append(entry)
    for entry in remove_entrys:
        self.existing_entries.discard(entry)
    print(self.existing_entries)
