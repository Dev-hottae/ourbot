

class org_data():
    def __init__(self):
        pass


    # 타겟 가격 설정
    def set_target_price(self, market):
        prev_price_data = self.prev_data_request(self, market, 2)[1]

        close = prev_price_data["close"]
        high = prev_price_data["high"]
        low = prev_price_data["low"]

        param = eff_param()

        target_price = close + (high - low) * param

        return target_price