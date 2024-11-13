import os
import subprocess
import sys
import platform
import shutil

def detect_compiler():
    """Detect the system compiler."""
    system_platform = platform.system()
    if system_platform in ["Linux", "Darwin"]:
        compiler = shutil.which("g++")
        if compiler:
            return "g++"
        else:
            raise EnvironmentError("No suitable C++ compiler found on Linux or macOS.")
    elif system_platform == "Windows":
        compiler = shutil.which("g++") or shutil.which("cl")
        if compiler:
            return compiler
        else:
            raise EnvironmentError("No suitable C++ compiler found on Windows.")
    else:
        raise EnvironmentError("Unknown platform")

def get_binary_name(prog_name):
    """Get the appropriate binary name based on the operating system."""
    return f"{prog_name}.exe" if platform.system() == "Windows" else prog_name

def load_bldfile(bldfilename="Bldfile"):
    """Load and parse the build file, returning program configuration dictionaries."""
    progdic, srcdic, bindic, filedic, optdic = {}, {}, {}, {}, {}
    try:
        with open(bldfilename, "r") as bldfile:
            for line in bldfile:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if '=' in line:
                    id, value = line.split('=', maxsplit=1)
                    if id == 'prog':
                        progdic[value] = value
                        prog = value
                    elif id == 'src':
                        srcdic[prog] = value
                    elif id == 'bin':
                        bindic[prog] = value
                    elif id == 'file':
                        filedic[prog] = value
                    elif id == 'option':
                        optdic[prog] = value
    except FileNotFoundError:
        print(f"Error: {bldfilename} does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {bldfilename}: {e}")
        sys.exit(1)

    return progdic, srcdic, bindic, filedic, optdic

def prepare_directories(bindir):
    """Ensure the binary directory exists, creating it if necessary."""
    if not bindir:
        raise ValueError("Binary directory path is missing.")
    try:
        os.makedirs(bindir, exist_ok=True)
    except Exception as e:
        print(f"Error creating binary directory '{bindir}': {e}")
        sys.exit(1)

def validate_sources(srcdir, files):
    """Validate that the source directory and files exist."""
    if not os.path.isdir(srcdir):
        print(f"Error: Source directory '{srcdir}' does not exist.")
        sys.exit(1)
    source_files = [os.path.join(srcdir, f) for f in files.split() if os.path.isfile(os.path.join(srcdir, f))]
    if not source_files:
        print("Error: No valid source files found.")
        sys.exit(1)
    return source_files

def validate_options(options):
    return ' '.join(options.split(';'))

def compile_program(compiler, source_files, output_path, options):
    """Compile the program using the specified compiler and source files."""
    compile_command = [compiler] + source_files + ["-g", "-o", output_path, options]
    try:
        print(f"Compiling {output_path}...")
        print(f"Compile command {compile_command}...")
        subprocess.run(compile_command, check=True)
        print(f"Build successful! Binary created at {output_path}")
    except subprocess.CalledProcessError:
        print("Error: Compilation failed.")
        sys.exit(1)

def main():
    """Main function to orchestrate the build process."""
    progdic, srcdic, bindic, filedic,optdic = load_bldfile()
    compiler = detect_compiler()

    for prog in progdic:
        outbin = get_binary_name(prog)
        srcdir = srcdic.get(prog)
        bindir = bindic.get(prog)
        files = filedic.get(prog)
        option = optdic.get(prog)

        if not files:
            print(f"Error: No source files listed for program '{prog}'.")
            sys.exit(1)

        # Prepare directories and validate files
        prepare_directories(bindir)
        source_files = validate_sources(srcdir, files)

        # Define the output path for the binary
        output_path = os.path.join(bindir, outbin)

        #define option
        options = validate_options(option)

        # Compile the program
        compile_program(compiler, source_files, output_path, options)

if __name__ == "__main__":
    main()
