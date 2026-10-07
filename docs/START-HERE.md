# Start here: Group 1, first week

Goal of the week: everyone has run the mock chain on their laptop, the squads are set, and we know
what has to be ordered or clarified. **The rig will not be here before mid-November, probably later.**
No task this week needs hardware, and neither do most of the next six weeks: README section 3b lists
what to do for each task while you wait.

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

| squad | members | tasks |
|---|---|---|
| 1: Capture and data | Master 1 (lead), Bachelor 1, Bachelor 2 | rig and setup guide, readers for the three simulators, ROS 2 data flow, data pipeline, lap files, part of the dashboard |
| 2: Timing, models and AI | Master 2 (lead), Bachelor 3, Bachelor 4 | clocks, setups and the delay model, local AI models, cameras, raw inputs and heart rate, part of the dashboard |

## How the weeks run

Read [WORKFLOW.md](WORKFLOW.md) today: set up your group's fork, a team meeting among yourselves
every week, a pull request to me every Friday, a call with me every second week.

## Thursday to Friday

5. Read the README, sections 1 to 3b. Each person writes down three things in the guide that are
   unclear, in `notes/week-01.md`.
6. **Squad 2, task 4:** measure the clock offset between two of your laptops (README, phase 5), once
   with `chrony` or `w32tm`. Write down how you measured and what you got, with the uncertainty.
   You are inventing the method you will use on the real machines.
7. **Squad 1, task 5:** install ROS 2 Jazzy (a container is fine), publish the mock stream on a
   topic, record it with `ros2 bag record`, replay it. Does it keep the timestamps?
8. **Squad 1, task 6:** sketch the data pipeline on paper: the stages, and what a stored session
   contains (samples, who drove, which simulator, clock offset, software versions).
9. **Squad 2, task 8:** run `python -m simlab.latency`, change one stage in the code and explain
   the change in the output.
10. **Squad 2, task 10:** install a model server on a laptop (llama.cpp, Ollama or vLLM), run one
    small model, and write down how long an answer takes and how much memory it uses.
11. Open a pull request with your notes in `notes/week-01.md`. First merged pull request.

## Before the first weekly meeting

12. Squad 1: for each of the three games (rFactor 2, Assetto Corsa, iRacing), write down what you expect to
    read and at what rate, and which game you expect to recommend, as a hypothesis. Task 3 tests it. Luke
    hands over his reader code for the games at the start of that task.
13. Everyone: five questions for Group 2 about the lap format ([INTERFACE.md](INTERFACE.md)). Group 2's
    squad 2 is drafting the contract with you.
14. Luke needs from you: the list of accounts and licences the rig needs and who will own them.

## If you are stuck

Ask in the group channel before spending more than 30 minutes. Hardware questions go to Luke.
