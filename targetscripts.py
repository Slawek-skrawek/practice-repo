# import os
import subprocess
import traceback

# Path containing the Mynewt project
PROJECTS_DIR = "~/work/myproj"
# Path containing the Mynewt bsp directories
BSP_DIR = "@apache-mynewt-core/hw/bsp/"
BOOT_BUILD_PROFILE = "optimized"
BUILD_PROFILE = "debug"

def run_cmd(cmd, check=True):
    """Runs a shell command and returns (success, output)."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        traceback.print_exc()
        return False, e.stderr

def target_exists(name):
    success, _ = run_cmd(f"newt target show {name}", check=False)
    return success

def create_target(board_name, app_name):
    target_name = board_name + "-" + app_name
    if not target_exists(target_name):
        print(f"Creating target: {target_name}")
        run_cmd(f"newt target create {target_name}")
        run_cmd(f"newt target set {target_name} app=apps/{app_name}")
        run_cmd(f"newt target set {target_name} bsp={BSP_DIR}{board_name}")
        run_cmd(f"newt target set {target_name} build_profile={BUILD_PROFILE}")
    else:
        print(f"Target {target_name} already exists.")

    print(f" Building target: {target_name}")
    success, output = run_cmd(f"newt build {target_name}", check=False)
    # print(output)
    if not success:
        print(f" Build failed for {target_name}:\n{output}")
        return

    print(f" Creating image for target: {target_name}")
    success, output = run_cmd(f"newt create-image {target_name} timestamp", check=False)
    # print(output)
    if not success:
        print(f" Image creation failed for {target_name}:\n{output}")
        return

def main():
            run_cmd(f"cd {PROJECTS_DIR}")
    #for entry in os.scandir(BSP_DIR):
        #if entry.is_dir():
            board_name = "nordic_pca10040" #pic32mx470_6lp_clicker
            #board_name = entry.name
            print(f"\nProcessing target: {board_name}")

            target_name_boot = board_name + "-boot"
            if not target_exists(target_name_boot):
                print(f"Creating target: {target_name_boot}")
                run_cmd(f"newt target create {target_name_boot}")
                run_cmd(f"newt target set {target_name_boot} app=mcuboot/boot/mynewt")
                run_cmd(f"newt target set {target_name_boot} bsp={BSP_DIR}{board_name}")
                run_cmd(f"newt target set {target_name_boot} build_profile={BOOT_BUILD_PROFILE}")
            else:
                print(f"Target {target_name_boot} already exists.")

            print(f" Building target: {target_name_boot}")
            success, output = run_cmd(f"newt build {target_name_boot}", check=False)
            # print(output)
            if not success:
                print(f" Build failed for {target_name_boot}:\n{output}")
                # continue

            create_target(board_name, "blinky")

            create_target(board_name, "watchdog")

            print(f"Done with {board_name}")
            print("-" * 40)

if __name__ == "__main__":
    main()
