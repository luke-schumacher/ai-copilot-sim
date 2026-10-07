# Start here: Group 1, first week

Goal of the week: everyone has run the mock chain on their laptop, the squads are set,
and we know what has to be ordered or clarified. **The rig will not be here before
mid-November, probably later.** No task this week needs hardware, and neither do most of the
next six weeks: README section 3b lists what to do for each task while you wait.

## Wednesday 7 October (kickoff day)

1. Read [DATA-RULE.md](DATA-RULE.md). Everyone agrees to it in the room.
2. Choose roles and squads (below) and a weekly meeting slot.
3. One person forks this repository and adds the group; everyone clones the fork **and**
   `ai-copilot-lab` next to it, then sets up as in the README, phase 0, step 1.
   `uv run pytest` must pass.
4. Run `python -m simlab.mock_source out.jsonl` and open `out.jsonl`. Find `source_t` and
   `receive_t`. Why are there two?

## Squads

Each Master leads a squad of three.

| squad | members | focus |
|---|---|---|
| A: Capture and data | M1 (lead), B1, B2 | rig and setup guide, the three sims, ROS 2, lap files, labelled sessions |
| B: Timing, models and AI | M2 (lead), B3, B4 | clocks, the latency model, cameras, the AI machine, heart rate |

## Thursday to Friday

5. Read the README, sections 1 to 3 and 6. Each person writes down three things in the guide
   that you do not understand yet, as comments on an issue "Guide questions".
6. **Squad B:** measure the clock offset between two of your laptops (README, phase 5), once
   with `chrony` or `w32tm`. Write down how you measured and what you got, with the uncertainty.
   You are inventing the method S4 will use on the real machines.
7. **Squad A:** install ROS 2 Jazzy (a container is fine), publish the mock stream on a topic,
   record it with `ros2 bag record`, replay it. Does it keep the timestamps?
8. **Squad B:** run `python -m simlab.latency`, then change one stage in the code and explain the
   change in the output. Where do the 20 ms come from in "slow processing"?
9. Open a pull request with your notes in `notes/week1-<your name>.md`. First merged pull request.

## Before the first weekly meeting

10. Squad A: list, for each of the three sims, what you expect to be able to read and at
    what rate, as a hypothesis. S2 and S3 will test it.
11. Everyone: write down five questions for Group 2 about the lap format
    ([INTERFACE.md](INTERFACE.md)). Group 2's squad B is drafting the contract with you.
12. Luke needs from you: the list of accounts and licences the rig needs (rFactor 2, Assetto
    Corsa and iRacing are in the proposal) and who will own them.

## How the weeks run

Read [WORKFLOW.md](WORKFLOW.md) today: set up your group's fork, a team meeting among yourselves
every week, a pull request to me every Friday, a call with me every second week.

## If you are stuck

Ask in the group channel before spending more than 30 minutes. Hardware questions and anything
about data go to Luke.
