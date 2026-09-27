from app.db import Base, engine
from app.seed import seed_benchmarks, seed_inventory
from app.demo import load_demo_html
from app.db import SessionLocal
from app import models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_benchmarks(db)
        seed_inventory(db)
        load_demo_html(db)
        print("Veritabanı ve demo müfredat hazır.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
