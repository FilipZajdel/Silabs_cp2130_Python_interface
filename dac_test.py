from dac import Dac

if __name__ == "__main__":
    dac = Dac()

    while True:
        inp = input()
        if int(inp) > -1 and int(inp) < 3301:
            dac.currentVoltage = int(inp)
            print(f"Voltage set to {inp} mV")