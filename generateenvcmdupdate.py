import subprocess
import yaml
import argparse
import re

# Function to get installed conda packages
def get_conda_packages(env_current, exact_match=False, no_version=False):
    # Get conda package list with versions
    result = subprocess.run(['conda', 'list','-n',env_current,'--export'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception("Failed to get conda package list.")
    conda_packages = result.stdout.decode().splitlines()

    pip_packages = []
    if no_version:
#        return [pkg.split('=')[0] for pkg in conda_packages if not pkg.startswith('#')]  # Only package names, no versions        
        pip_packages = [pkg.split('=')[0] for pkg in conda_packages if 'pypi' in pkg and not pkg.startswith('#')]  # Only package names, no versions
    elif exact_match:
#        return [pkg for pkg in conda_packages if not pkg.startswith('#')]  # Include full version and build
        pip_packages = [pkg for pkg in conda_packages if 'pypi' in pkg and not pkg.startswith('#')]  # Include full version and build    
    else:
        pip_packages = [pkg.split('=')[0] + '=' + pkg.split('=')[1] for pkg in conda_packages if 'pypi' in pkg and not pkg.startswith('#')]  # Package and version
#        return [pkg.split('=')[0] + '=' + pkg.split('=')[1] for pkg in conda_packages if not pkg.startswith('#')]  # Package and version        
    
    true_conda_packages = []
    if no_version:
#        return [pkg.split('=')[0] for pkg in conda_packages if not pkg.startswith('#')]  # Only package names, no versions        
        true_conda_packages = [pkg.split('=')[0] for pkg in conda_packages if 'pypi' not in pkg and not pkg.startswith('#')]  # Only package names, no versions
    elif exact_match:
#        return [pkg for pkg in conda_packages if not pkg.startswith('#')]  # Include full version and build
        true_conda_packages = [pkg for pkg in conda_packages if 'pypi' not in pkg and not pkg.startswith('#')]  # Include full version and build    
    else:
        true_conda_packages = [pkg.split('=')[0] + '=' + pkg.split('=')[1] for pkg in conda_packages if 'pypi' not in pkg and not pkg.startswith('#')]  # Package and version
#        return [pkg.split('=')[0] + '=' + pkg.split('=')[1] for pkg in conda_packages if not pkg.startswith('#')]  # Package and version        
    return (true_conda_packages,pip_packages)

# Function to get installed pip packages
def get_pip_packages(no_version=False):
    # Get pip package list with versions
    result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception("Failed to get pip package list.")
    pip_packages = result.stdout.decode().splitlines()

    if no_version:
#        return [pkg.split(r'[=@]')[0] for pkg in pip_packages]  # Only package names, no versions        
#        return [pkg.split('==')[0] for pkg in pip_packages]  # Only package names, no versions
        return [re.split(r'[=@]',pkg)[0].strip() for pkg in pip_packages]  # Only package names, no versions
    else:
        return pip_packages

# Function to generate environment.yml
def generate_environment_yml(env_current, env_name='my_environment', python_version='3.8', exact_match=False, no_version=False, conda_packages=None, pip_packages=None):
    if conda_packages is None:
        (conda_deps,pip_deps) = get_conda_packages(env_current, exact_match, no_version)
#    if pip_packages is None:
#        pip_packages = get_pip_packages(no_version)
#    print(pip_packages)
    # Split conda and pip packages
#    conda_deps = []
#    pip_deps = []

#    for package in conda_packages:
#        if 'pypi' in package:  # These are pip-managed packages
#            pip_deps.append(package.split('=')[0])
#        else:
#            conda_deps.append(package)
#    print(pip_deps)
    
    if no_version:
        pip_packages = [re.split(r'[=@]',pkg)[0].strip() for pkg in pip_deps]  # Only package names, no versions
    else:
        pip_packages = pip_deps
#    print("FORMATTED:")
#    print(pip_packages)
    # Create the environment.yml structure
    env_yaml = {
        'name': env_name,
        'channels': [
            'defaults',
            'conda-forge'
        ],
        'dependencies': []
    }

    # If using --no_version, ensure Python version is included
    if no_version:
        env_yaml['dependencies'].append(f'python={python_version}')

    # Add conda dependencies
    env_yaml['dependencies'] += conda_deps

    # Add pip as a dependency if there are pip packages
    if pip_packages:
 #       print('appending pip deps')
#        env_yaml['dependencies'].update(pip_deps)
        env_yaml['dependencies'].append('pip')  # Ensure pip is listed as a dependency
        env_yaml['dependencies'].append({'pip': pip_packages})  # Add pip packages under pip: section

    # Write to a file without comments
    with open('environment.yml', 'w') as f:
        yaml.dump(env_yaml, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print("environment.yml has been successfully generated!")

# Main function to parse command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Generate an environment.yml file for Conda environment.")

    parser.add_argument('--env_current', type=str, default='base', help="Name of the current environment to export")    
    parser.add_argument('--env_name', type=str, default='my_environment', help="New name of the environment")
    parser.add_argument('--python_version', type=str, default='3.8', help="Specify Python version (required for --no_version)")
    parser.add_argument('--exact_match', action='store_true', help="Include exact version and build information")
    parser.add_argument('--no_version', action='store_true', help="Include only package names, no version info")
    
    args = parser.parse_args()

    # Ensure that --python_version is used only with --no_version
    if args.no_version and not args.python_version:
        print("Error: You must specify a Python version with --python_version when using --no_version.")
        return

    try:
        generate_environment_yml(
            env_current=args.env_current,
            env_name=args.env_name,
            python_version=args.python_version,
            exact_match=args.exact_match,
            no_version=args.no_version
        )
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
