from statemachine import Machine
from statemachine.reachable import reachable


@Machine(init_state='stop')
class Player:
    def __init__(self, video):
        self.video = video

    @reachable(from_states=['pause', 'stop'])
    def start(self):
        ...

    @reachable(from_states=['start'])
    def pause(self):
        ...

    @reachable(from_states=['start', 'pause'])
    def stop(self):
        ...


p = Player('some video here')

p.start()
p.pause()
p.start()
p.stop()
p.start()
p.stop()
p.start()

print(p.find_all_states('start'))