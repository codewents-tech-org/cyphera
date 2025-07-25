"""
Module: Description Model
File: model.py
Layer: Data / Persistence Layer
Component ID:
Requirement IDs:
Author: Vijaya Ragavan
Created On: 2025-06-27
Version:

Purpose:
--------
Provides `DescriptionModel`, a reusable persistence wrapper around SQLAlchemy
for storing and retrieving HTML content using the central schema manager.

Responsibilities:
-----------------
• Load and save HTML content to a given SQLAlchemy model
• Uses `schema_manager.py` for all DB access
• Accepts configurable model and field names

Methods & Returns:
------------------
__init__(model_class, id_column, content_column)
  • Configures the ORM model and field mappings

load(record_id)
  • Returns HTML content string or empty string

save(html_content, record_id)
  • Returns True on success, False on failure
"""

from controllers.schema_manager import get_instances, create_instance, update_instance ,get_first_instance

class DescriptionModel:
    """
    Generic ORM-based description model using schema_manager for read/write.
    """

    def __init__(self, model_class, id_column: str, content_column: str):
        """
        Args:
            model_class: SQLAlchemy model class (e.g., ScopeDescriptionORM)
            id_column: Primary key column name (e.g., 'scope_id')
            content_column: HTML content field name (e.g., 'scope_content')
        """
        self.model_class = model_class
        self.id_column = id_column
        self.content_column = content_column

    def load(self, record_id: int = 1) -> str:
        """
        Load HTML content from the database.

        Args:
            record_id: The ID to fetch.

        Returns:
            HTML content string or "" if not found.
        """
        filters = {self.id_column: record_id}
        print("testing 111111111----------------------------------------------------------")
        instance = get_first_instance(self.model_class, filters)
        print("testing 222222222----------------------------------------------------------")
        return getattr(instance, self.content_column, "") if instance else ""

    def save(self, html_content: str, record_id: int = 1, user: str = "system") -> bool:
            """
            Save or update HTML content in the database.

            Args:
                html_content: The content string to store.
                record_id: The row ID to insert/update.
                user: Username or identifier performing the operation.

            Returns:
                True if successful, False otherwise.
            """
            filters = {self.id_column: record_id}
            instance = get_first_instance(self.model_class, filters)

            if instance:
                return update_instance(self.model_class, filters, {
                    self.content_column: html_content,
                    "updated_by": user
                })
            else:
                new_instance = self.model_class(**{
                    self.id_column: record_id,
                    self.content_column: html_content,
                    "created_by": user,
                    "updated_by": user
                })
                return bool(create_instance(new_instance))

