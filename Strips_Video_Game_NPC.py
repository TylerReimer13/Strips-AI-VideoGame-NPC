from copy import deepcopy
from datetime import datetime

# Actions = [take_cover, throw_grenade, shoot, move, call_backup, retreat]
# States = [in_cover, player_alive, at(X), playerAt(Y), alone]


class State:
    def __init__(self, health=None, at=None, in_cover=None, num_grenades=None, has_gun=None):
        self.health = health
        self.at = at
        self.in_cover = in_cover
        self.num_grenades = num_grenades
        self.prev = None
        self.action = None
        self.uuid = None
        self.prev_uuid = None
        self.next_uuids = {}

    # Note: Add self.action == other.action to this check if we wish to record multiple ways to generate same state
    # This adds more unique states, and thus more time to fins solution.
    def __eq__(self, other):
        return self.health == other.health and self.at == other.at and self.in_cover == other.in_cover \
               and self.num_grenades == other.num_grenades

    def __repr__(self):
        return self.action + ", " + self.uuid


# --------------------- ACTION PRECONDITIONS ---------------------

# state is the entire state of the world at present time, a and b are entities (npc or player)
def take_cover_pre(state, a, b, location):
    return state.in_cover[a] is False


def exit_cover_pre(state, a, b, location):
    return state.in_cover[a] is True


def throw_grenade_pre(state, a, b, location):
    return state.num_grenades[a] > 0 and state.in_cover[a] is False


def move_pre(state, a, b, location):
    return state.in_cover[a] is False and state.at[a] != location


def shoot_pre(state, a, b, location):
    return state.at[a] == state.at[b]


# ------------------------ ACTION EFFECTS ------------------------

def take_cover_effect(state, a, b, location):
    state.prev = deepcopy(state)
    state.prev_uuid = state.uuid
    state.in_cover[a] = True
    state.action = "Take_Cover"
    return state


def exit_cover_effect(state, a, b, location):
    state.prev = deepcopy(state)
    state.prev_uuid = state.uuid
    state.in_cover[a] = False
    state.action = "Exit_Cover"
    return state


def throw_grenade_effect(state, a, b, location):
    state.prev = deepcopy(state)
    state.prev_uuid = state.uuid

    state.num_grenades[a] = max(0, state.num_grenades[a] - 1)
    if state.in_cover[b] is False:
        state.health[b] = 'low'
    state.action = "Throw_Grenade"
    return state


def move_effect(state, a, b, location):
    state.prev = deepcopy(state)
    state.prev_uuid = state.uuid
    state.at[a] = location
    state.action = "Move_To: " + location
    return state


def shoot_effect(state, a, b, location):
    state.prev = deepcopy(state)
    state.prev_uuid = state.uuid
    if state.health[b] == 'low':
        state.health[b] = 'dead'
    elif state.health[b] == 'full':
        state.health[b] = 'low'
    state.action = "Shoot"
    return state

# ----------------------------------------------------------------


def check_goal_found(current, goal):
    if current.health['player'] == goal.health['player']:
        return True

    return False


def find_prev(curr, all_states):
    for state in all_states:
        if state == curr.prev:
            return state


def find_state_by_uuid(states, uuid):
    for state in states:
        if state.uuid == uuid:
            return state


def backtrack(curr, start, all_states):
    # Start at the goal state, and backtrack the sequence of actions to get to the start state. Currently there is no
    # heuristic metric implemented, so the backtracking just uses the first state encountered in the back track.

    action_list = []
    while not curr == start:
        action = curr.action
        action_list.append(action)
        # curr = curr.prev
        curr = find_prev(curr, all_states)
    return action_list[::-1]


def find_plan(init, goal, preconditions, actions):
    # Currently uses BFS to search all possible state-action pairs. Currently, the 'state space' can contain duplicate
    # values for current position, given that the previous positions were different

    states_queue = [init]
    states = [init]
    locations = ['loc1', 'loc2']

    n_iter = 0
    uuid_ctr = 1
    while states_queue:
        n_iter += 1
        current = states_queue[0]

        if check_goal_found(current, goal_state):
            print('***************************************************************************************')
            print('************************************* FOUND GOAL **************************************')
            print('***************************************************************************************')
            print('STATES: ', len(states), "  Num iter: ", n_iter)

            plan = backtrack(current, curr_state, states)
            return plan, states

        for location in locations:
            for i, action in enumerate(actions):
                if preconditions[i](current, 'npc', 'player', location):
                    ns = action(deepcopy(current), 'npc', 'player', location)
                    ns.uuid = str(uuid_ctr)
                    uuid_ctr += 1

                    if ns not in states:
                        states.append(ns)
                        states_queue.append(ns)

        states_queue.pop(0)

    print('STATES: ', len(states), "  Num iter: ", n_iter)
    # for st in states:
    #     print("Curr UUID: ", st.uuid, "  Prev UUID: ", st.prev_uuid, "Next UUIDS: ", st.next_uuids)

    return [], states


if __name__ == "__main__":
    startTime = datetime.now()

    curr_state = State(
                       health={'npc': 'full', 'player': 'full'},
                       at={'npc': 'loc1', 'player': 'loc2'},
                       in_cover={'npc': True, 'player': False},
                       num_grenades={'npc': 2, 'player': 0},
                       )

    curr_state.uuid = "0"
    curr_state.action = "None"

    goal_state = State(
                       health={'player': 'dead'}
                       )

    pre_funcs = [exit_cover_pre, take_cover_pre, shoot_pre, move_pre, throw_grenade_pre]
    action_funcs = [exit_cover_effect, take_cover_effect, shoot_effect, move_effect, throw_grenade_effect]

    action_plan, final_states = find_plan(curr_state, goal_state, pre_funcs, action_funcs)

    print('TIME: ', datetime.now() - startTime)

    print('--------------- ACTION PLAN ---------------')
    print(action_plan)
