# Python State Machines
This is an extremely small and new library I wrote to help manage state machines in classes in Python.

## Inspiration
This library was inspired by [this talk](https://www.youtube.com/watch?v=I1Mzx_tSpew). I found the concept very fascinating, as I have run into this problem many times, but I also found the syntax clunky. 
One of the nice things about Python is its dynamism. This can be a real struggle when size and complexity grows, but it at least
allows for very nice, often magical feeling, syntax around a lot of things. Naturally, rather than passing large, *in situ* lists and dictionaries, I thought it would be 
nicer to employ dictionaries, and some inference to make the code more pleasant and (hopefully) more self-documenting

## Find on pypi

This project uses [this template](https://github.com/fastai/pypi_template) to create a pypi package. 

You can find the project [here](https://pypi.org/project/statemachine-elunico/) and install it using `pip install statemachine-elunico` and then import it with `import statemachine`

## Explanation 
The library consists of 3 main items: `Machine`, `MachineError`, and `allow_access`.

`Machine` is a decorator that provides a class with the logic needed to implement a finite state machine. 
This class can then be used to guard access to particular
methods in *your* class without you having to write any `if` based logic.
This allows all the business logic of your program to live in the methods you write unclutters, 
while still allowing a robust state management system  to exist around method calls in your class. 
The logic for handling the state checking and changing is done by the `Machine` while you add a simple 
declarative decorator statement to the methods you want checked when defining them. 
Watching the talk given in the above link and looking at the example file might be a good way of getting a feel for how this works. 


### Explanation through Example

Briefly, imagine you have a music player that be be started, stopped, and paused and so has the methods `start`, `stop`, and `pause`.
You want to be able to pause while started but not stopped. You want to be able to stop while either started, paused, or stopped. Finally,
you want to be able to start while stopped or paused. You begin in the stopped state.

Immediately, you might be able to see there is a fair bit going on, and we only have 3 states and a few rules. 
You can imagine how much more complex this might get if we have more options for states and the ways of moving between them.
In order to implement these rules, we could imagine a `Player` class with a source URL for the video it will play and 
several booleans for state. It would be the task of the creator of the `Player` class, then, to maintain the proper state 
of all these booleans and to ensure they are correctly checked and updated in every method. Once again, I will point
to the talk in the link I included for an idea of what this looks like (spoiler alert: it is not pretty)

This is where this library comes in. Rather than focus on the state management and checking, we leave that 
to the `Machine` class. It can take care of changing state and all the management and checking needed (mostly, 
more on that in a bit)

We simply use the `@Machine` annotation and then write our `Player` class
completely normally. We must also specify what our initial state will be. This will be true for every instance of a class

```python 
@Machine(init_state='stop')
class Player:
    def __init__(self, src: str):
        self.src = src
        
    def start(self):
        ...
        # business logic to start playing
     
    def stop(self):
        ...
        # business logic to stop playing
    
    def pause(self):
        ... 
        # business logic to pause playing
```

### Important Note

Let me point out several things before we continue: 1) the use of strings is a deliberate, but noteworthy choice. It is critical that you specify States 
to the machine as strings, however these strings must **exactly** match the names of methods which trigger those states in your class.
For example, here, the initial state is called 'stop' because the state 'stop' is always triggered by calling the `stop` method. 
We could not call this state 'stopped' unless we also called the method `stopped`. Doing it this way (while risky) **greatly** simplifies the code 
needed to implement and maintain. Because more time will be spent using the methods than the states themselves (since the `Machine` manages state logic)
I recommend you write methods as normal and have grammatically dubious state names rather than the other way around.
### ---

There is still something missing from this example. While we have created the machine and defined the initial state, we are
currently not guarding access to the methods of the class in any way. 
Using this library allows you to have unlimited methods that do not interact or pay any attention to the 
state machine. The state machine will only protect access to calling methods on which you have explicitly chosen 
to define limitations. 

These limitations are defined using the `allows_access` decorator. You 
add this decorator to the methods on the class which interact with the state machine. 
It accepts 1 keyword argument: an iterable of strings (`Iterable[str]`).
These strings **must exactly match the names of the states which are valid _source_ states for the particular method
being called**. What does this mean? Put simply, you define the states *from which* it is legal to transition 
to the state indicated by your method. Once again, the *names of methods* are used to indicate the destination
state and are used to set the current state after a method call. Therefore, it is important that you correctly name
the methods in the decorator. We will now see the class example from above, but fully written out to implement 
the state checking logic described in the beginning of the article. 

Note that because you are only passing strings into the decorators, it is trivially easy to allow transitions 
to the state being defined by the method by simply including the name of the method in the list of valid 'from states'

```python
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
```

Imagine now we create a `Player` object. This object begins in the 'stop' state. We may only call `start` from the 
'stop' state, as it is the only method whose `from_states` list includes 'stop'. Calling the `start` method 
will not only check to make sure we are in an acceptable state, but it will also transition the Machine to the 
'start' state, meaning it is no longer valid to call `start` but is valid to call `pause` and `stop` 

In the event that a method call cannot be executed due to the state machine's current state, then a `MachineError`
is raised and **the current state of the machine is unchanged**

The library also allows you to define a `to_states` parameter. This allows you to define the states that can be 
*transitioned to* from a paritcular method/state rather than transitioned from. You can also mix and match these
as you like in the same decorator, but **do not double up `allows_access` decorators on 1 method.

Here is another way of implementing the same logic above

```python
@Machine(init_state='stop')
class Player:
    def __init__(self, video):
        self.video = video

    @allows_access(from_states=['pause', 'stop'], to_states=['pause'])
    def start(self):
        ...

    @allows_access(to_states=['start', 'stop'])
    def pause(self):
        ...

    @allows_access(from_states=['start', 'pause', 'stop'])
    def stop(self):
        ...
```

You do not have to provide both `from_states` and `to_states`. It is possible to define every transition using only 
1 of these keyword arguments. Both exist simply to make it easier to express the most natural description of the 
domain. 

**There are no protections in place if you make a state that is inescapable or one that can never be reached. 
Note that if you do not decorate a method it will always be callable, but if it is decorated there are no checks for 
islands or cycles or deadends, that is up to you**

## Wrapping up 

I believe this implementation is elegant, concise, declarative, and easy to use. 

There is one more thing we can talk about. You can interrogate the machine to find out what methods are valid 
'to' states and valid 'from' states for a given state. When using the `@Machine` decorator
a method called `get_all_states` is injected into your decorated class. This method accepts a single `str` argument which is the 
name of the state/method you are interested in. It returns a `dict` object with two keys: the 'from_states' key 
maps to a set of strings that are all the states you may transition to the given state from and the 'to_states' 
key which maps to a set of all the valid next states for that state. 

You can say something like

```python
p = Player()
p.get_all_states('start') # returns {'to_states': {'pause', 'stop'}, 'from_states': {'pause', 'stop'}}
```
