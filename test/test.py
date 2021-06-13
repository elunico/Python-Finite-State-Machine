from statemachine import Machine
from statemachine.accesscontrol import allows_access


@Machine(init_state='stop')
class Player:
    def __init__(self, video):
        self.video = video

    @allows_access(from_states=['pause', 'stop'])
    def start(self):
        ...

    @allows_access(from_states=['start'])
    def pause(self):
        ...

    @allows_access(from_states=['start', 'pause', 'stop'])
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
p.stop()
p.stop()
p.stop()

print(p.get_all_states('start'))
print(p.get_all_states('stop'))
print(p.get_all_states('pause'))
