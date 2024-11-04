import time
import random
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import func

# Database connection
DATABASE_URL = "sqlite:///example.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# User Model


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())
    age = Column(Integer)
    address = Column(String)

# Product Model


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, server_default=func.now())
    description = Column(String)
    quantity = Column(Integer)

# Category Model


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())
    description = Column(String)
    parent_id = Column(Integer, ForeignKey('categories.id'))


# Create tables
Base.metadata.create_all(engine)


def insert_data(num_users=100000, num_products_per_user=2, num_categories=100, batch_size=1000):
    """Insert user, product, and category data."""
    session = Session()

    # Add categories in bulk
    categories = [
        {"name": f'Category {i}', "description": f'Description for Category {i}'}
        for i in range(num_categories)
    ]
    session.execute(Category.__table__.insert(), categories)

    # Add users and products in bulk
    users = []
    products = []

    for i in range(num_users):
        user = {"name": f'User {i}', "email": f'user{i}@example.com',
                "age": random.randint(18, 70), "address": f'Address {i}'}
        users.append(user)

        # Create several products for each user
        for j in range(num_products_per_user):
            product = {"name": f'Product {j} of User {i}', "price": random.uniform(10, 100), "user_id": i,
                       "description": f'Description for Product {j} of User {i}', "quantity": random.randint(1, 50)}
            products.append(product)

        # Commit in batches
        if (i + 1) % batch_size == 0:
            session.execute(User.__table__.insert(), users)
            session.execute(Product.__table__.insert(), products)
            users.clear()
            products.clear()

    # Insert remaining users and products
    if users:
        session.execute(User.__table__.insert(), users)
    if products:
        session.execute(Product.__table__.insert(), products)

    session.commit()
    session.close()


def update_data(batch_size=1000):
    """Randomly update users and products in batches."""
    session = Session()

    # Get all user IDs and product IDs for faster access
    user_ids = [user.id for user in session.query(User).all()]
    product_ids = [product.id for product in session.query(Product).all()]

    updates = []
    for _ in range(1000):  # Prepare 1000 updates
        # Update a random user
        user_id = random.choice(user_ids)
        updates.append({
            "id": user_id,
            "name": f'Updated User {user_id}',
            "age": random.randint(18, 70),
            "address": f'Updated Address'
        })

        # Update a random product
        product_id = random.choice(product_ids)
        updates.append({
            "id": product_id,
            "price": random.uniform(10, 100),
            "description": f'Updated Description for Product {product_id}',
            "quantity": random.randint(1, 50)
        })

        # Commit updates in batches
        if len(updates) >= batch_size:
            # Separate updates for users and products
            user_updates = [
                update for update in updates if 'user_id' in update]
            product_updates = [
                update for update in updates if 'product_id' in update]
            session.bulk_update_mappings(User, user_updates)
            session.bulk_update_mappings(Product, product_updates)
            updates.clear()

    # Apply any remaining updates
    if updates:
        user_updates = [update for update in updates if 'user_id' in update]
        product_updates = [
            update for update in updates if 'product_id' in update]
        session.bulk_update_mappings(User, user_updates)
        session.bulk_update_mappings(Product, product_updates)

    session.commit()
    session.close()


def delete_data(batch_size=1000):
    """Randomly delete users and products in batches."""
    session = Session()

    # Get all user IDs and product IDs for faster access
    user_ids = [user.id for user in session.query(User).all()]
    product_ids = [product.id for product in session.query(Product).all()]

    deletes = []
    for _ in range(1000):  # Prepare 1000 deletions
        # Delete a random user
        user_id = random.choice(user_ids)
        deletes.append({"id": user_id, "type": "user"})

        # Delete a random product
        product_id = random.choice(product_ids)
        deletes.append({"id": product_id, "type": "product"})

        # Commit deletions in batches
        if len(deletes) >= batch_size:
            user_deletes = [d['id'] for d in deletes if d['type'] == "user"]
            product_deletes = [d['id']
                               for d in deletes if d['type'] == "product"]

            # Delete users
            if user_deletes:
                session.query(User).filter(User.id.in_(user_deletes)).delete(
                    synchronize_session=False)

            # Delete products
            if product_deletes:
                session.query(Product).filter(Product.id.in_(
                    product_deletes)).delete(synchronize_session=False)

            deletes.clear()

    # Apply any remaining deletions
    if deletes:
        user_deletes = [d['id'] for d in deletes if d['type'] == "user"]
        product_deletes = [d['id'] for d in deletes if d['type'] == "product"]

        # Delete users
        if user_deletes:
            session.query(User).filter(User.id.in_(user_deletes)
                                       ).delete(synchronize_session=False)

        # Delete products
        if product_deletes:
            session.query(Product).filter(Product.id.in_(
                product_deletes)).delete(synchronize_session=False)

    session.commit()
    session.close()


if __name__ == "__main__":
    start_time = time.time()

    # Insert data
    insert_data()
    print(
        f"Insert operation completed. Time: {time.time() - start_time:.2f} seconds.")

    # Update operation
    update_data()
    print(
        f"Update operation completed. Time: {time.time() - start_time:.2f} seconds.")

    # Delete operation
    delete_data()
    print(
        f"Delete operation completed. Time: {time.time() - start_time:.2f} seconds.")
