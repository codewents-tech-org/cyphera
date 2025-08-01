"""
📦 Module        : schema_manager.py
🧱 Layer         : controllers
🔖 Module ID     : 
📋 Requirement ID(s): 
🧑‍💻 Developed By : Vijay
🕒 Created On    : 2025-05-14
🧾 File Version  : v1.0.1
🧾 Updated by    : Vijay
🧾 Updated on    : 2025-05-15

🧠 Description:
Centralized schema and database object manager. Provides interfaces for
create, read, update, delete (CRUD) operations using SQLAlchemy ORM.

🎯 Responsibilities:
- Perform CRUD operations on database tables
- Use decorators for session handling, and exception management
- Coordinate schema initialization and database migrations
- Auto-log actions using log_crud_action
"""
from asyncio.log import logger
import time
import os
import uuid
from datetime import datetime
from controllers.database import get_engine_and_session, Base
from controllers.database import handle_db_session, db_error_handler
#from components.logger_config import log_crud_action
from sqlalchemy import inspect, text , update
from controllers.database import get_engine_and_session
# ---------------------------------------------------------------------
# Schema Manager - Centralized DB Operations with Clean Architecture
# ---------------------------------------------------------------------

# @log_crud_action(
#     "CREATE",
#     module_name_getter=lambda *args, **kwargs: args[0].__class__.__name__,
#     entity_id_getter=lambda result, *args, **kwargs: getattr(result, 'id', '-')
# )



@db_error_handler
@handle_db_session
def create_instance(instance, session=None):
  
    import time

    for attempt in range(3):
        try:
            print(f"[⚙️ Attempt {attempt+1}] Adding instance with ID {getattr(instance, 'scope_id', '-')}")
            session.add(instance)
            session.commit()

            # Eager load and detach
            for column in inspect(instance).mapper.column_attrs:
                getattr(instance, column.key)
            session.expunge(instance)
            return instance

        except Exception as e:
            print(f"[DB Insert Failed] Attempt {attempt + 1}: {e}")
            session.rollback()
            if "database is locked" in str(e):
                time.sleep(0.8)  # slightly longer pause
            else:
                break

    print("[❌ FATAL] All retries failed. Aborting create_instance.")
    raise RuntimeError("Could not insert due to persistent DB lock.")





# @log_crud_action(
#     "READ",
#     module_name_getter=lambda *args, **kwargs: args[0].__name__,
#     entity_id_getter=lambda result, *args, **kwargs: (
#         f"{len(result)} rows" if isinstance(result, list) else "1 row"
#     )
# )


@db_error_handler
@handle_db_session
def get_first_instance(model, filters=None, session=None):
    query = session.query(model)
    if filters:
        query = query.filter_by(**filters)

    result = query.first()

    if result:
        # ✅ Eager load all columns
        for column in inspect(result).mapper.column_attrs:
            getattr(result, column.key)

        # ✅ Detach from session
        session.expunge(result)

    return result

@db_error_handler
@handle_db_session
def get_instances(model, filters=None, session=None):
    query = session.query(model)
    if filters:
        query = query.filter_by(**filters)

    results = query.all()

    # ✅ Force eager loading of all attributes
    for obj in results:
        for column in inspect(obj).mapper.column_attrs:
            getattr(obj, column.key)

    # ✅ Detach from session so objects are safe after session closes
    for obj in results:
        session.expunge(obj)

    return results  # ✅ ORM instances safe to use like Django

@db_error_handler
@handle_db_session
def get_unique_instances(model, filters=None, session=None):
    query = session.query(model)
    if filters:
        query = query.filter_by(**filters)

    results = query.distinct().all()
    distinct_values = [row[0] for row in results if row[0] is not None]
    
    return distinct_values

# @log_crud_action(
#     "UPDATE",
#     module_name_getter=lambda *args, **kwargs: args[0].__name__,
#     entity_id_getter=lambda result, *args, **kwargs: result
# )
@db_error_handler
@handle_db_session
def update_instance(model, filter_by, update_data, session=None):
    """
    Updates an existing database record.
    """
    instance = session.query(model).filter_by(**filter_by).first()
    if instance:
        for key, value in update_data.items():
            setattr(instance, key, value)
        return True
    return False

@db_error_handler
@handle_db_session
def update_all_instances(model, filter_by, update_data, session=None):
    """
    Updates an existing database record.
    """
    instances = session.query(model).filter_by(**filter_by).all()
    for instance in instances:
        if instance:
            for key, value in update_data.items():
                setattr(instance, key, value)
    return False


# @log_crud_action(
#     "DELETE",
#     module_name_getter=lambda *args, **kwargs: args[0].__name__,
#     entity_id_getter=lambda result, *args, **kwargs: result
# )
@db_error_handler
@handle_db_session
def delete_instance(model, filters, session=None):
    """
    Deletes a database record based on filters.
    """
    instance = session.query(model).filter_by(**filters).first()
    if instance:
        session.delete(instance)
        return True
    return False

@db_error_handler
@handle_db_session
def delete_all_instance(model, filters, session=None):
    """
    Delete a database records based on filters.
    """
    instances = session.query(model).filter_by(**filters).all()
    print(instances)
    for instance in instances:
        if instance:
            session.delete(instance)
    return False

@db_error_handler
def initialize_database():
    """
    Initializes all ORM tables in the connected database.
    """
    engine, _ = get_engine_and_session()
    Base.metadata.create_all(bind=engine)
    return True
def print_all_table_summaries():
    engine, session_cls = get_engine_and_session()
    session = session_cls()  # ✅ create an actual session instance

    inspector = inspect(engine)

    print("\n[📊 Table Summaries]")

    for table_name in inspector.get_table_names():
        print(f"\n🔹 Table: {table_name}")

        # Get column names
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        print(f"   Columns: {columns}")

        # Get row count
        try:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"   Total Rows: {count}")
        except Exception as e:
            print(f"   ⚠️ Error querying {table_name}: {e}")

    session.close()

@db_error_handler
@handle_db_session
def get_max_numeric_suffix(model, column_name, prefix="", session=None):
    """
    Finds the highest numeric suffix for values like 'PREFIX-1', 'PREFIX-12', etc.
    
    Args:
        model: SQLAlchemy ORM model class.
        column_name: String name of the column (e.g., 'asset_id').
        prefix: Expected string prefix in the values (e.g., 'AST', 'ASSET').

    Returns:
        Integer maximum number found. If none, returns 0.
    """
    column_attr = getattr(model, column_name, None)
    if column_attr is None:
        print(f"[ERROR] Column '{column_name}' not found in model {model.__name__}")
        return 0

    query = session.query(column_attr).filter(column_attr.like(f"{prefix}-%"))
    values = [getattr(row, column_name) for row in query.all()]

    max_num = 0
    for val in values:
        if val and val.startswith(f"{prefix}-"):
            try:
                num = int(val.split(f"{prefix}-")[-1])
                max_num = max(max_num, num)
            except ValueError:
                continue

    return max_num

@handle_db_session
@db_error_handler
def bulk_update_instances(model, update_data_list, filter_key="uuid", session=None):
    """
    Performs bulk update on model instances using a common filter_key (default: uuid).

    Args:
        model: SQLAlchemy ORM model class
        update_data_list: List of dicts. Each dict must include the filter_key + update fields.
        filter_key: Field name used for identifying records (default: 'uuid')
        session: Injected DB session (handled by @handle_db_session)
    """
    if not update_data_list:
        logger.info("⛔ No data to update.")
        return
    print("check bulk update instances working or not 111111111111")
    try:
        for original_data in update_data_list:
            data = original_data.copy()  # Avoid mutating original list
            filter_val = data.pop(filter_key, None)
            if filter_val is None:
                logger.warning(f"⚠️ Skipping update, missing {filter_key} in: {original_data}")
                continue

            stmt = (
                update(model)
                .where(getattr(model, filter_key) == filter_val)
                .values(**data)
            )
            session.execute(stmt)

        session.commit()
        logger.info(f"✅ Bulk updated {len(update_data_list)} instances of {model.__name__}")

    except Exception as e:
        logger.exception(f"❌ Bulk update failed for model {model.__name__}")
        session.rollback()
        raise


@db_error_handler
@handle_db_session
def bulk_insert_instances(instances: list, session=None) -> None:
    """
    Inserts a list of ORM instances into the database in bulk.

    Args:
        instances (list): List of SQLAlchemy ORM model instances.
        session (Session, optional): Injected by handle_db_session.

    Raises:
        Exception: If commit or flush fails, exception is logged and re-raised.
    """
    # if not instances:
    #     return

    # try:
    #     session.bulk_save_objects(instances)
    #     session.commit()
    # except Exception as e:
    #     session.rollback()
    if not instances:
        return

    # Assign UUIDs if missing
    for obj in instances:
        if not hasattr(obj, "uuid"):
            raise AttributeError(f"❌ Object {obj} is missing 'uuid' attribute.")
        if not getattr(obj, "uuid"):
            print("am in......")
            setattr(obj, "uuid", str(uuid.uuid4()))

    try:
        session.bulk_save_objects(instances)
        session.commit()

    except Exception as e:
        session.rollback()
        raise






@db_error_handler
@handle_db_session
def bulk_upsert_instances(model, data_list, key_field='uuid', session=None):
    """
    Performs bulk upsert (insert or update) for SQLAlchemy ORM models.
    If the row with the key exists, it updates, else inserts.

    Args:
        model: SQLAlchemy ORM model class.
        data_list: List of dicts, each representing row data.
        key_field: The primary or unique key column (default 'uuid').
        session: DB session (injected).
    """
    for data in data_list:
        key_val = data.get(key_field)
        obj = session.query(model).filter(getattr(model, key_field)==key_val).first()
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = model(**data)
            session.add(obj)
    session.commit()


@db_error_handler
@handle_db_session
def delete_instances_like(model, field_name, like_pattern, session=None):
    """
    Bulk delete ORM records where the specified field matches a LIKE pattern.

    Args:
        model: The ORM model class.
        field_name: The string name of the field (e.g., 'node_id').
        like_pattern: The SQL LIKE pattern (e.g., 'TH-1_node%').
        session: Injected session.

    Returns:
        int: Number of rows deleted.
    """
    column = getattr(model, field_name)
    query = session.query(model).filter(column.like(like_pattern))
    count = query.count()
    query.delete(synchronize_session=False)
    return count


# schema_manager.py or utility ORM updates
def bulk_update_leaf_text(model, node_types, leaf_id, new_text):
    """
    Updates the 'text' field for all rows in the model where node_type is in node_types and text starts with 'leaf_id '.
    """
    engine, session_cls = get_engine_and_session()
    session = session_cls()
    try:
        for node_type in node_types:
            session.query(model).filter(
                and_(
                    model.node_type == node_type
                    # model.text.like(f"{leaf_id} %")
                )
            ).update({"text": new_text}, synchronize_session=False)
        session.commit()
    finally:
        session.close()


@db_error_handler
@handle_db_session
def bulk_update_instances_with_like(model, field_name, like_pattern, update_data, session=None):
    """
    Bulk update ORM records where the specified field matches a LIKE pattern.
    """
    column = getattr(model, field_name)
    stmt = (
        update(model)
        .where(column.like(like_pattern))
        .values(**update_data)
    )
    session.execute(stmt)
    session.commit()


def bulk_delete_with_like_and_types(session, model, like_field, like_value, node_types):
    """
    Bulk delete where `like_field` LIKE `like_value` and node_type in `node_types`
    """
    # Example: like_field = 'node_id', like_value = '12 %', node_types = ['leaf', ...]
    like_column = getattr(model, like_field)
    query = session.query(model).filter(
        model.node_type.in_(node_types),
        like_column.like(like_value)
    )
    print(f"[DEBUG][DELETE] Deleting {query.count()} rows from {model.__tablename__} where node_type in {node_types} and {like_field} LIKE '{like_value}'")
    query.delete(synchronize_session=False)
    session.commit()


@db_error_handler
@handle_db_session
def get_instances_like(model, column_name, like_pattern, extra_filters=None, session=None):
    column = getattr(model, column_name)
    query = session.query(model).filter(column.like(like_pattern))
    if extra_filters:
        query = query.filter_by(**extra_filters)
    results = query.all()
    for obj in results:
        for col in inspect(obj).mapper.column_attrs:
            getattr(obj, col.key)
        session.expunge(obj)
    return results

def safe_get_instances(model, filters=None):
    """
    Wrapper around get_instances that removes 'is_deleted' for models that don't support it.
    """
    filters = filters or {}

    if model.__name__ == "RiskData" and "is_deleted" in filters:
        filters = {k: v for k, v in filters.items() if k != "is_deleted"}

    return get_instances(model, filters)

