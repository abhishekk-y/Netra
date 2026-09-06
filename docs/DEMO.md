# Demo Script

## Running the Demo
1. Open a terminal and navigate to the project root.
2. Ensure the system is running (`./start.sh`).
3. Run the Judge Mode Controller:
   ```bash
   python -m demo.judge_mode
   ```
4. Follow the interactive prompts to execute the 6 phases:
   - **Phase 1**: Baseline training.
   - **Phase 2**: Reconnaissance (simulates port scans).
   - **Phase 3**: Credential Access (simulates brute force).
   - **Phase 4**: Lateral Movement (simulates east-west spread).
   - **Phase 5**: C2 (simulates beaconing).
   - **Phase 6**: Exfiltration (simulates data leakage).
5. Watch the Frontend UI update in real-time as each phase progresses.
