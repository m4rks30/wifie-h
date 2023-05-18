import subprocess
import os
import re
from collections import namedtuple
import configparser
def get_windows_saved_ssids():
    output = subprocess.check_output("netsh wlan show profiles").decode()
    ssids = []
    profiles = re.findall(r"All User Profile\s(.*)", output)
    for profile in profiles:
        ssid = profile.strip().strip(":").strip()
        ssids.append(ssid)
    return ssids
def get_windows_saved_wifi_passwords(verbose=1):
    ssids = get_windows_saved_ssids()
    Profile = namedtuple("Profile", ["ssid", "ciphers", "key"])
    profiles = []
    for ssid in ssids:
        ssid_details = subprocess.check_output(f"""netsh wlan show profile "{ssid}" key=clear""").decode()
        # get the ciphers
        ciphers = re.findall(r"Cipher\s(.*)", ssid_details)
        # clear spaces and colon
        ciphers = "/".join([c.strip().strip(":").strip() for c in ciphers])
        # get the Wi-Fi password
        key = re.findall(r"Key Content\s(.*)", ssid_details)
        try:
            key = key[0].strip().strip(":").strip()
        except IndexError:
            key = "None"
        profile = Profile(ssid=ssid, ciphers=ciphers, key=key)
        if verbose >= 1:
            print_windows_profile(profile)
        profiles.append(profile)
    return profiles
def print_windows_profile(profile):
    print(f"{profile.ssid:25}{profile.ciphers:15}{profile.key:50}")
def print_windows_profiles(verbose):
    print("SSID                     CIPHER(S)      KEY")
    get_windows_saved_wifi_passwords(verbose)
def get_linux_saved_wifi_passwords(verbose=1):   
    network_connections_path = "/etc/NetworkManager/system-connections/"
    fields = ["ssid", "auth-alg", "key-mgmt", "psk"]
    Profile = namedtuple("Profile", [f.replace("-", "_") for f in fields])
    profiles = []
    for file in os.listdir(network_connections_path):
        data = { k.replace("-", "_"): None for k in fields }
        config = configparser.ConfigParser()
        config.read(os.path.join(network_connections_path, file))
        for _, section in config.items():
            for k, v in section.items():
                if k in fields:
                    data[k.replace("-", "_")] = v
        profile = Profile(**data)
        if verbose >= 1:
            print_linux_profile(profile)
        profiles.append(profile)
    return profiles
def print_linux_profile(profile):
    print(f"{str(profile.ssid):25}{str(profile.auth_alg):5}{str(profile.key_mgmt):10}{str(profile.psk):50}") 
def print_linux_profiles(verbose):
    print("SSID                     AUTH KEY-MGMT  PSK")
    get_linux_saved_wifi_passwords(verbose)
def print_profiles(verbose=1):
    if os.name == "nt":
        print_windows_profiles(verbose)
    elif os.name == "posix":
        print_linux_profiles(verbose)
    else:
        raise NotImplemented("Code only works for either Linux or Windows")
if __name__ == "__main__":
    print_profiles()
