import json

pp = json.dumps([{"ticket": "UNIQUE_TICKET"}, {"type": "orderbook",
                                                                  "codes": 'code_list'
                                                                  }])


print(pp)