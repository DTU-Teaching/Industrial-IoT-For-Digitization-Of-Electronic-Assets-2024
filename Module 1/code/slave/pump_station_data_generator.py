import csv
import datetime
import logging
import random
import time

import numpy as np


class PumpSignalGenerator:
    def __init__(self, alternation_interval, save_data=False):
        self.alternation_interval = alternation_interval
        self.save_data = save_data
        self.current_pump = 1  # Start with Pump 1
        self.pump1_speed = 0
        self.pump2_speed = 0
        self.sigma_noise = 0.1
        self.mean_noise = 0
        self.counter = 1

        self.pump1_rpm_lags = np.array([0, 0, 0])
        self.outflow_p1_lags = np.array([0, 0, 0])
        self.power_p1_lags = np.array([0, 0, 0])
        self.pump2_rpm_lags = np.array([0, 0, 0])
        self.outflow_p2_lags = np.array([0, 0, 0])
        self.power_p2_lags = np.array([0, 0, 0])

        if self.save_data:
            self.csv_file = open('./pump_speeds.csv', mode='w', newline='')
            self.writer = csv.writer(self.csv_file)
            self.writer.writerow(
                ["time", "pump1_rpm", "pump1_power", "pump1_outflow", "pump2_rpm", "pump2_power", "pump2_outflow"])

    def smooth_speed(self, previous_speed):
        """ Generates the next speed level based on the previous speed. """
        min_speed, max_speed = 900, 1500
        delta = random.randint(2, 20)

        if previous_speed == min_speed:
            next_speeds = [min_speed, min_speed + delta]
        elif previous_speed == max_speed:
            next_speeds = [max_speed - delta, max_speed]
        else:
            next_speeds = [previous_speed - delta, previous_speed, previous_speed + delta]

        return np.random.choice(next_speeds)

    @staticmethod
    def speed_to_outflow_model(speed_lags, outflow_lags, efficiency=1):
        """ Speed to outflow model """
        if np.any(speed_lags == 0):
            return efficiency * (0.35 * speed_lags[-1] + 0.085 * outflow_lags[-1])

        else:
            return efficiency * (0.12 * speed_lags[0] + 0.2 * speed_lags[1] + 0 * speed_lags[2] +
                                 0.12 * outflow_lags[0] + 0.02 * outflow_lags[1] + 0 * outflow_lags[
                                     2]) + np.random.normal(0, 0.1)

    @staticmethod
    def speed_to_power_model(speed_lags, power_lags, efficiency=1):
        """ Speed to power model """
        if np.any(power_lags == 0):
            return efficiency * (0.00004 * speed_lags[-1] ** 2)
        else:
            return efficiency * (0.00004 * speed_lags[0] ** 2 + 0.00015 * speed_lags[1] + 0 * speed_lags[2] +
                                 0.00005 * power_lags[0] + 0.0001 * power_lags[1] + 0 * power_lags[
                                     2]) + np.random.normal(0, 0.2)

    def apply_signals(self, pump1_speed, pump2_speed):
        if self.pump1_speed == 0:
            self.pump1_rpm_lags = np.array([0, 0, 0])
            self.outflow_p1_lags = np.array([0, 0, 0])
            self.power_p1_lags = np.array([0, 0, 0])

        self.pump1_rpm_lags = np.roll(self.pump1_rpm_lags, shift=-1)
        self.pump1_rpm_lags[-1] = self.pump1_speed

        outflow_p1 = self.speed_to_outflow_model(self.pump1_rpm_lags, self.outflow_p1_lags, efficiency=0.80)
        power_p1 = self.speed_to_power_model(self.pump1_rpm_lags, self.power_p1_lags, efficiency=0.87)

        self.outflow_p1_lags = np.roll(self.outflow_p1_lags, shift=-1)
        self.outflow_p1_lags[-1] = outflow_p1

        self.power_p1_lags = np.roll(self.power_p1_lags, shift=-1)
        self.power_p1_lags[-1] = power_p1

        self.pump1_speed = pump1_speed

        if self.pump2_speed == 0:
            self.pump2_rpm_lags = np.array([0, 0, 0])
            self.outflow_p2_lags = np.array([0, 0, 0])
            self.power_p2_lags = np.array([0, 0, 0])

        self.pump2_rpm_lags = np.roll(self.pump2_rpm_lags, shift=-1)
        self.pump2_rpm_lags[-1] = self.pump2_speed

        outflow_p2 = self.speed_to_outflow_model(self.pump2_rpm_lags, self.outflow_p2_lags, efficiency=0.98)
        power_p2 = self.speed_to_power_model(self.pump2_rpm_lags, self.power_p2_lags, efficiency=0.87)

        self.outflow_p2_lags = np.roll(self.outflow_p2_lags, shift=-1)
        self.outflow_p2_lags[-1] = outflow_p2

        self.power_p2_lags = np.roll(self.power_p2_lags, shift=-1)
        self.power_p2_lags[-1] = power_p2

        self.pump2_speed = pump2_speed
        time.sleep(1)
        return pump1_speed, power_p1, outflow_p1, pump2_speed, power_p2, outflow_p2

    def reset(self):
        self.pump1_rpm_lags = np.array([0, 0, 0])
        self.outflow_p1_lags = np.array([0, 0, 0])
        self.power_p1_lags = np.array([0, 0, 0])
        self.pump2_rpm_lags = np.array([0, 0, 0])
        self.outflow_p2_lags = np.array([0, 0, 0])
        self.power_p2_lags = np.array([0, 0, 0])
        self.pump1_speed = 0
        self.pump2_speed = 0

    def generate_signal(self):
        """ Simulation of a pump station with two pumps alternating each self.alternation_interval interval"""
        if self.current_pump == 1:
            if self.pump1_speed == 0:
                self.pump1_rpm_lags = np.array([0, 0, 0])
                self.outflow_p1_lags = np.array([0, 0, 0])
                self.power_p1_lags = np.array([0, 0, 0])
                self.pump1_speed = np.random.randint(1000, 1400)

            self.pump1_rpm_lags = np.roll(self.pump1_rpm_lags, shift=-1)
            self.pump1_rpm_lags[-1] = self.pump1_speed

            outflow_p1 = self.speed_to_outflow_model(self.pump1_rpm_lags, self.outflow_p1_lags, efficiency=0.80)
            power_p1 = self.speed_to_power_model(self.pump1_rpm_lags, self.power_p1_lags, efficiency=0.87)

            self.outflow_p1_lags = np.roll(self.outflow_p1_lags, shift=-1)
            self.outflow_p1_lags[-1] = outflow_p1

            self.power_p1_lags = np.roll(self.power_p1_lags, shift=-1)
            self.power_p1_lags[-1] = power_p1

            self.pump1_speed = self.smooth_speed(self.pump1_speed)
            self.pump2_speed, outflow_p2, power_p2 = 0, 0, 0

        elif self.current_pump == 2:
            if self.pump2_speed == 0:
                self.pump2_rpm_lags = np.array([0, 0, 0])
                self.outflow_p2_lags = np.array([0, 0, 0])
                self.power_p2_lags = np.array([0, 0, 0])
                self.pump2_speed = np.random.randint(1000, 1400)

            self.pump2_rpm_lags = np.roll(self.pump2_rpm_lags, shift=-1)
            self.pump2_rpm_lags[-1] = self.pump2_speed

            outflow_p2 = self.speed_to_outflow_model(self.pump2_rpm_lags, self.outflow_p2_lags, efficiency=0.98)
            power_p2 = self.speed_to_power_model(self.pump2_rpm_lags, self.power_p2_lags, efficiency=0.87)

            self.outflow_p2_lags = np.roll(self.outflow_p2_lags, shift=-1)
            self.outflow_p2_lags[-1] = outflow_p2

            self.power_p2_lags = np.roll(self.power_p2_lags, shift=-1)
            self.power_p2_lags[-1] = power_p2

            self.pump2_speed = self.smooth_speed(self.pump2_speed)
            self.pump1_speed, outflow_p1, power_p1 = 0, 0, 0

        if self.save_data:
            self.writer.writerow([datetime.datetime.now(), self.pump1_speed, power_p1, outflow_p1,
                                  self.pump2_speed, power_p2, outflow_p2])
        time.sleep(1)
        logging.info(
            f"Pump 1 Speed: {self.pump1_speed:.2f}, Pump 1 Power: {power_p1:.2f}, Pump 1 Outflow: {outflow_p1:.2f}, Pump 2 Speed: {self.pump2_speed:.2f}, Pump 2 Power: {power_p2:.2f}, Pump 2 Outflow: {outflow_p2:.2f}")

        # Wait for 1 second, simulating the reading from PLC

        # Alternate pumps at every self.alternation_interval
        if self.counter % self.alternation_interval == 0:
            self.current_pump = 2 if self.current_pump == 1 else 1

        self.counter += 1

        return self.pump1_speed, power_p1, outflow_p1, self.pump2_speed, power_p2, outflow_p2
