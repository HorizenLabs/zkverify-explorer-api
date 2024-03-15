"""Removed Transfer.

Revision ID: b9199a8338bd
Revises: 6d1caa771eba
Create Date: 2022-12-13 14:04:01.285092

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from dotenv import load_dotenv
import sys, os
sys.path = ['', '..', '../..'] + sys.path[1:]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_file = ".env"
if os.path.exists(".local.env"):
    env_file = ".local.env"


load_dotenv(os.path.join(BASE_DIR, "../..", env_file))
sys.path.append(BASE_DIR)

# Mock required settings to run this migration which depends on user settings
class settings:
    DB_USERNAME = os.environ['DB_USERNAME']
    DB_NAME = os.environ['DB_NAME']
    DB_HARVESTER_NAME = os.environ['DB_HARVESTER_NAME'] or "polkascan"


# revision identifiers, used by Alembic.
revision = 'b9199a8338bd'
down_revision = '6d1caa771eba'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_transfers`")
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_explorer_transfer_block_hash', table_name='explorer_transfer')
    op.drop_index('ix_explorer_transfer_block_number', table_name='explorer_transfer')
    op.drop_index('ix_explorer_transfer_complete', table_name='explorer_transfer')
    op.drop_index('ix_explorer_transfer_event_idx', table_name='explorer_transfer')
    op.drop_index('ix_explorer_transfer_extrinsic_idx', table_name='explorer_transfer')
    op.drop_index('ix_explorer_transfer_from_multi_address_account_id', table_name='explorer_transfer')
    op.drop_index('ix_explorer_transfer_to_multi_address_account_id', table_name='explorer_transfer')
    op.drop_table('explorer_transfer')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('explorer_transfer',
    sa.Column('block_number', mysql.INTEGER(unsigned=True), autoincrement=False, nullable=False),
    sa.Column('event_idx', mysql.INTEGER(unsigned=True), autoincrement=False, nullable=False),
    sa.Column('extrinsic_idx', mysql.INTEGER(unsigned=True), autoincrement=False, nullable=True),
    sa.Column('from_multi_address_type', mysql.VARCHAR(length=16), nullable=True),
    sa.Column('from_multi_address_account_id', sa.BINARY(length=32), nullable=True),
    sa.Column('from_multi_address_account_index', mysql.INTEGER(unsigned=True), autoincrement=False, nullable=True),
    sa.Column('from_multi_address_raw', sa.VARBINARY(length=255), nullable=True),
    sa.Column('from_multi_address_address_32', sa.BINARY(length=32), nullable=True),
    sa.Column('from_multi_address_address_20', sa.BINARY(length=20), nullable=True),
    sa.Column('to_multi_address_type', mysql.VARCHAR(length=16), nullable=True),
    sa.Column('to_multi_address_account_id', sa.BINARY(length=32), nullable=True),
    sa.Column('to_multi_address_account_index', mysql.INTEGER(unsigned=True), autoincrement=False, nullable=True),
    sa.Column('to_multi_address_raw', sa.VARBINARY(length=255), nullable=True),
    sa.Column('to_multi_address_address_32', sa.BINARY(length=32), nullable=True),
    sa.Column('to_multi_address_address_20', sa.BINARY(length=20), nullable=True),
    sa.Column('value', mysql.DECIMAL(unsigned=True, precision=65, scale=0), nullable=True),
    sa.Column('block_datetime', mysql.DATETIME(), nullable=True),
    sa.Column('block_hash', sa.BINARY(length=32), nullable=False),
    sa.Column('complete', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.CheckConstraint('(`complete` in (0,1))', name='explorer_transfer_chk_1'),
    sa.PrimaryKeyConstraint('block_number', 'event_idx'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_explorer_transfer_to_multi_address_account_id', 'explorer_transfer', ['to_multi_address_account_id'], unique=False)
    op.create_index('ix_explorer_transfer_from_multi_address_account_id', 'explorer_transfer', ['from_multi_address_account_id'], unique=False)
    op.create_index('ix_explorer_transfer_extrinsic_idx', 'explorer_transfer', ['extrinsic_idx'], unique=False)
    op.create_index('ix_explorer_transfer_event_idx', 'explorer_transfer', ['event_idx'], unique=False)
    op.create_index('ix_explorer_transfer_complete', 'explorer_transfer', ['complete'], unique=False)
    op.create_index('ix_explorer_transfer_block_number', 'explorer_transfer', ['block_number'], unique=False)
    op.create_index('ix_explorer_transfer_block_hash', 'explorer_transfer', ['block_hash'], unique=False)
    # ### end Alembic commands ###
    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_transfers`")
    op.execute(f"""
                CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl_explorer_transfers`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
                BEGIN
                        # GLOBAL SETTINGS
                        SET @block_start = `block_start`;
                        SET @block_end = `block_end`;
                        SET @update_status = `update_status`;

                        INSERT INTO `{settings.DB_NAME}`.`explorer_transfer` (
                                            `block_number`,
                                            `event_idx`,
                                            `extrinsic_idx`,
                                            `from_multi_address_type`,
                                            `from_multi_address_account_id`,
                                            `to_multi_address_type`,
                                            `to_multi_address_account_id`,
                                            `value`,
                                            `block_datetime`,
                                            `block_hash`,
                                            `complete`
                        )(
                                    SELECT
                                            `cbev`.`block_number` AS `block_number`,
                                            `cbev`.`event_idx` AS `event_idx`,
                                            `cbev`.`extrinsic_idx` AS `extrinsic_idx`,
                                            0 AS `from_multi_address_type`,
                                            UNHEX(RIGHT(JSON_UNQUOTE(`cbev`.`data`->"$.event.attributes[0]"),64)) AS `from_multi_address_account_id`,
                                            0 AS `to_multi_address_type`,
                                            UNHEX(RIGHT(JSON_UNQUOTE(`cbev`.`data`->"$.event.attributes[1]"),64)) AS `to_multi_address_account_id`,
                                            JSON_UNQUOTE(`cbev`.`data`->"$.event.attributes[2]") AS `value`,
                                            `cbts`.`datetime` AS `block_datetime`,
                                            `cbev`.`block_hash` AS `block_hash`,
                                            `cbev`.`complete` AS `complete`
                                    FROM `{settings.DB_HARVESTER_NAME}`.`codec_block_event` AS `cbev`
                                    INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_header` AS `nbh` ON `cbev`.`block_hash` = `nbh`.`hash` AND `nbh`.`block_number` >= @block_start AND	`nbh`.`block_number` <= @block_end
                                    INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_runtime` AS `nbr` ON `cbev`.`block_hash` = `nbr`.`hash` AND `nbr`.`block_number` >= @block_start AND	`nbr`.`block_number` <= @block_end
                                    INNER JOIN `{settings.DB_HARVESTER_NAME}`.`codec_block_timestamp` AS `cbts` ON `cbev`.`block_hash` = `cbts`.`block_hash` AND `cbts`.`block_number` >= @block_start AND	`cbts`.`block_number` <= @block_end
                                    WHERE	`cbev`.`block_number` >= @block_start AND	`cbev`.`block_number` <= @block_end
                                    AND `cbev`.`event_module`='Balances' AND `cbev`.`event_name`='Transfer'
                        ) ON DUPLICATE KEY UPDATE
                                        `extrinsic_idx` = VALUES(`extrinsic_idx`),
                                        `from_multi_address_type` = VALUES(`from_multi_address_type`),
                                        `from_multi_address_account_id` = VALUES(`from_multi_address_account_id`),
                                        `to_multi_address_type` = VALUES(`to_multi_address_type`),
                                        `to_multi_address_account_id` = VALUES(`to_multi_address_account_id`),
                                        `value` = VALUES(`value`),
                                        `block_datetime` = VALUES(`block_datetime`),
                                        `block_hash` = VALUES(`block_hash`),
                                        `complete` = VALUES(`complete`)
                        ;

                                ### UPDATE STATUS TABLE ###
                                IF @update_status = 1 THEN
                                        INSERT INTO `{settings.DB_NAME}`.`harvester_status` (`key`,`description`,`value`)(
                                                SELECT
                                                        'PROCESS_ETL_EXPLORER_TRANSFERS' AS	`key`,
                                                        'Max blocknumber of etl process' AS `description`,
                                                        CAST(@block_end AS JSON) AS `value`
                                                LIMIT 1
                                        ) ON DUPLICATE KEY UPDATE
                                                `description` = VALUES(`description`),
                                                `value` = VALUES(`value`)
                                        ;
                                END IF;

                    END
            """)