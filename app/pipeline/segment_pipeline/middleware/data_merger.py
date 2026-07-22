import pandas as pd

# def merge_data(dqi, final, delivery):
#     master = pd.concat([delivery, dqi], axis=1)

#     # Get release and bounce frame
#     r = int(master["release_frame"][0])
#     b = int(master["bounce_frame"][0])

#     # Filter only frames between release and bounce
#     flight = final[(final["frame"] >= r) & (final["frame"] <= b)]

#     # Average 3D position during flight
#     master["avg_ball_x"] = flight["ball_x"].mean()
#     master["avg_ball_y"] = flight["ball_y"].mean()
#     master["avg_ball_z"] = flight["ball_z"].mean()

#     master["bowler_arm"] = final["bowler_arm"].mode()[0]

#     return master



def merge_data(final, delivery):

    master = pd.concat([delivery, final], axis=1)

    r = int(master["release_frame"][0])
    b = int(master["bounce_frame"][0])

    flight = final[
        (final["frame"] >= r) &
        (final["frame"] <= b)
    ]

    master["avg_ball_x"] = flight["ball_x"].mean()
    master["avg_ball_y"] = flight["ball_y"].mean()
    master["avg_ball_z"] = flight["ball_z"].mean()

    # master["bowler_arm"] = final["bowler_arm"].mode()[0]

    return master