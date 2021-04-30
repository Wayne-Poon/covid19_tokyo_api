import sys
import traceback
from flask import request
from common.pandas_man import DataFrameMan
from common.controller import Controller


def get_patients():
    controller = Controller()
    sm = controller.get_syslog_man()
    try:
        area = request.args.get('area')
        address = request.args.get('address')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        forced = request.args.get('forced')
        # Null排除
        forced = forced if forced else False

        offset = request.args.get('offset', type=int)
        limit = request.args.get('limit', type=int)

        option_keys = request.args.getlist('option_keys', lambda x: x.split(','))
        option_keys = list(controller.flatten(option_keys))
        print(f"options={option_keys}")

        option_values = request.args.getlist('option_values', lambda x: x.split(','))
        option_values = list(controller.flatten(option_values))
        print(f'values={option_values}')

        df = controller.get_dataframe(area, forced)
        conf_json = controller.get_config_json(area)
        df_man = DataFrameMan()

        df_man.change_date_type_to_datetime(df, conf_json["date_key"])
        df = df_man.find_records_within_period(df, conf_json["date_key"], start_date, end_date)
        df = df_man.find_records_by_address(df, conf_json["address_columns"], address)
        for k, v in zip(option_keys, option_values):
            df = df_man.search_dataframe_value(df, k, v)
        df = df_man.limit_records(df, offset, limit)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_log = traceback.extract_tb(exc_traceback)
        print(e, exc_type, exc_value, tb_log)
        msg = f'traceback={tb_log}, error_type{exc_type}, error_msg={exc_value}'
        sm.log(msg, 'error')
        return msg, 500
    return df_man.change_date_type_to_str(df, conf_json["date_key"]).to_dict(orient='records')
