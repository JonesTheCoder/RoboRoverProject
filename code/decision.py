import numpy as np


def calculate_steer(Rover):
    # Set steering to average angle clipped to the range +/- 15
    # if we actually lean a bit to the right, that should help us navigate
    # the terrain more completely by following one wall.  Lets try
    # taking the mean of the right half of the angles instead
    right_leaning_angles = sorted(Rover.nav_angles)[0:int(len(Rover.nav_angles)*0.75)]
    mean_angle = np.mean(np.array(right_leaning_angles) * (180/np.pi))

    if Rover.hard_turn and len(Rover.steer_history) >= Rover.max_steer_history_length:
        Rover.steer_clip_threshold = (np.mean(Rover.steer_history) - 0.25)

    return np.clip(mean_angle, -1 * Rover.steer_clip_threshold, Rover.steer_clip_threshold)


# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function
def decision_step(Rover):

    print("MODE:", Rover.mode)
    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward':
            # first, see if we're stuck....
            Rover.position_history.append(Rover.pos)
            if len(Rover.position_history) > Rover.max_history_length:
                Rover.position_history.popleft()
                total_delta = 0
                for i in range(len(Rover.position_history) - 1):
                    a_pos = Rover.position_history[i]
                    b_pos = Rover.position_history[i+1]
                    delta_x = np.abs(a_pos[0] - b_pos[0])
                    delta_y = np.abs(a_pos[1] - b_pos[1])
                    total_delta += (delta_x + delta_y)
                if total_delta <= Rover.stuck_threshold:
                    # we're stuck, put it in reverse and try again
                    Rover.mode = 'backward'
                    Rover.back_delta = 0
                    Rover.back_count = 0

            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:
                # If mode is forward, navigable terrain looks good
                # and velocity is below max, then throttle
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                Rover.steer = calculate_steer(Rover)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # clear position history so that we don't mistake stop for stuck
            Rover.position_history.clear()
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = calculate_steer(Rover)
                    Rover.mode = 'forward'
        elif Rover.mode == 'backward':
            delta_x = Rover.pos[0] - Rover.prev_pos[0]
            delta_y = Rover.pos[1] - Rover.prev_pos[1]
            Rover.back_delta += (np.abs(delta_x) + np.abs(delta_y))
            if Rover.back_delta < Rover.back_allowance:
                Rover.steer = 0
                Rover.throttle = -1 * Rover.throttle_set
            Rover.back_count += 1
            if Rover.back_delta > Rover.back_allowance or Rover.back_count > 50:
                Rover.mode = 'stop'
                Rover.back_delta = 0
                Rover.position_history.clear()



    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.position_history.clear()
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0

    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True

    Rover.prev_pos = Rover.pos
    if np.abs(Rover.steer) > 10:
        if Rover.hard_turn:
            Rover.steer_history.append(Rover.steer)
            if len(Rover.steer_history) > Rover.max_steer_history_length:
                Rover.steer_history.popleft()
        else:
            Rover.hard_turn = True
            Rover.steer_history.clear()
    elif np.abs(Rover.steer < 10) and Rover.hard_turn:
        Rover.hard_turn = False
        Rover.steer_history.clear()
        Rover.steer_clip_threshold = 15
    return Rover
