class RangeState(object):
    """We define a state object which provides some utility functions for the
    individual states within the state machine."""

    def __init__(self):
        print('Processing current state transition to', str(self))

    def on_event(self, two_range_bits):
        """Handle 2 range bits that are delegated to this RangeState."""
        pass

    def __repr__(self):
        """Leverages the __str__ method to describe the RangeState."""
        return self.__str__()

    def __str__(self):
        """Returns the name of the RangeState."""
        return self.__class__.__name__


class RangeA(RangeState):
    """Range A state for a particular axis."""

    def on_event(self, two_range_bits):
        if two_range_bits == 'pin_entered':
            return RangeB()
        return self


class RangeB(RangeState):
    """Range B state for a particular axis."""

    def on_event(self, two_range_bits):
        if two_range_bits == 'device_locked':
            return RangeA()
        return self


class SimpleDevice(object):
    """A simple state machine that mimics the functionality of a device from a high level."""

    def __init__(self):
        """Initialize the components."""
        self.state = RangeA()

    def on_event(self, two_range_bits):
        """This is the bread and butter of the state machine. Incoming events are delegated to the given states which
           then handle the two_range_bits. The result is then assigned as the new state."""
        self.state = self.state.on_event(two_range_bits)  # The next state will be the result of the on_event function.


if __name__ == '__main__':
    device = SimpleDevice()
    print(device.state)
    device.on_event('device_locked')
    print(device.state)
    device.on_event('pin_entered')
    print(device.state)
    device.on_event('device_locked')
    print(device.state)
    device.on_event('device_locked')
