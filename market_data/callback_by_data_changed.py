

class callback_by_data_changed():

    def __init__(self, initial_value):
        self._value = initial_value
        self._renew = None
        self._callbacks = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        old_value = self._value
        self._value = new_value
        self._notify_observers(old_value, new_value)

    def _notify_observers(self, old_value, new_value):
        for callback in self._callbacks:
            callback(old_value, new_value)

    def callback_by_changed(self, new_value):
        self._renew = new_value

def print_if_change_greater_than_500(old_value, new_value):
    if abs(old_value - new_value) > 500:
        print(f'The value changed by more than 500 (from {old_value} to {new_value})')


class zcallback_by_data_changed(object):
    def __init__(self):
        self._global_wealth = 10.0
        self._observers = []

    @property
    def global_wealth(self):
        return self._global_wealth

    @global_wealth.setter
    def global_wealth(self, value):
        self._global_wealth = value
        for callback in self._observers:
            print('announcing change')
            callback(self._global_wealth)

    def bind_to(self, callback):
        print('bound')
        self._observers.append(callback)