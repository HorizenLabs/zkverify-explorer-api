import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.explorer import Extrinsic
from app.settings import settings

# Create database connection
engine = create_engine(settings.API_SQLA_URI)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Helper function to generate random hex string
def random_hex(length):
    return '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(length * 2)])

# List of mock call modules and names
call_modules = ["balances", "staking", "system", "treasury"]
call_names = {
    "balances": ["transfer", "set_balance", "force_transfer"],
    "staking": ["bond", "unbond", "withdraw_unbonded"],
    "system": ["remark", "set_code", "set_storage"],
    "treasury": ["propose_spend", "reject_proposal", "approve_proposal"]
}

# Generate mock data
def create_mock_extrinsics(num_extrinsics):
    base_time = datetime.now(timezone.utc)
    for i in range(num_extrinsics):
        call_module = random.choice(call_modules)
        extrinsic = Extrinsic(
            block_number=random.randint(1, 1000000),
            extrinsic_idx=i % 100,
            hash=random_hex(32),
            version=4,
            call_module=call_module,
            call_name=random.choice(call_names[call_module]),
            signed=random.choice([True, False]),
            signature=random_hex(65),
            nonce=random.randint(0, 1000),
            era={"period": 64, "phase": 0},
            tip=random.randint(0, 1000000000),
            block_datetime=base_time - timedelta(minutes=i),
            block_hash=random_hex(32), 
            complete=True
        )
        session.add(extrinsic)
    
    session.commit()

# Add mock data
num_extrinsics = 1000  # Adjust this number as needed
create_mock_extrinsics(num_extrinsics)

print(f"Added {num_extrinsics} mock extrinsics to the database.")

# Close the session
session.close()
