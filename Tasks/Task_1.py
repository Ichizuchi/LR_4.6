#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET

@dataclass
class Flight:
    destination: str
    flight_number: str
    plane_type: str


@dataclass
class FlightSchedule:
    flights: List[Flight] = field(default_factory=list)

    def add_flight(self, destination: str, flight_number: str, plane_type: str) -> None:
        self.flights.append(Flight(destination, flight_number, plane_type))
        self.flights.sort(key=lambda flight: flight.destination)

    def __str__(self) -> str:
        # Создание таблицы для вывода
        table = []
        line = '+-{}-+-{}-+-{}-+'.format('-' * 20, '-' * 15, '-' * 15)
        table.append(line)
        table.append('| {:^20} | {:^15} | {:^15} |'.format("Город назначения", "Номер рейса", "Тип самолета"))
        table.append(line)
        for flight in self.flights:
            table.append('| {:<20} | {:<15} | {:<15} |'.format(flight.destination, flight.flight_number, flight.plane_type))
        table.append(line)
        return '\n'.join(table)

    def select_flights_by_plane_type(self, plane_type: str) -> List[Flight]:
        selected_flights = [flight for flight in self.flights if flight.plane_type == plane_type]
        return selected_flights

    def load_from_xml(self, filename: Path) -> None:
        if os.path.exists(filename):
            tree = ET.parse(filename)
            root = tree.getroot()
            self.flights = []
            for flight_element in root.findall('flight'):
                destination = flight_element.find('destination').text
                flight_number = flight_element.find('flight_number').text
                plane_type = flight_element.find('plane_type').text
                if destination and flight_number and plane_type:
                    self.flights.append(Flight(destination, flight_number, plane_type))

    def save_to_xml(self, filename: Path) -> None:
        root = ET.Element("flights")
        for flight in self.flights:
            flight_element = ET.Element("flight")
            destination_element = ET.SubElement(flight_element, "destination")
            destination_element.text = flight.destination
            flight_number_element = ET.SubElement(flight_element, "flight_number")
            flight_number_element.text = flight.flight_number
            plane_type_element = ET.SubElement(flight_element, "plane_type")
            plane_type_element.text = flight.plane_type
            root.append(flight_element)
        tree = ET.ElementTree(root)
        with open(filename, 'wb') as file:
            tree.write(file, encoding="utf-8", xml_declaration=True)


def input_flights(schedule: FlightSchedule) -> None:
    n = int(input("Введите количество рейсов: "))
    for _ in range(n):
        destination = input("Введите город назначения: ")
        flight_number = input("Введите номер рейса: ")
        plane_type = input("Введите тип самолета: ")
        schedule.add_flight(destination, flight_number, plane_type)


def print_flights_with_plane_type(schedule: FlightSchedule) -> None:
    plane_type = input("Введите тип самолета: ")
    selected_flights = schedule.select_flights_by_plane_type(plane_type)
    if selected_flights:
        for flight in selected_flights:
            print(f"Город назначения: {flight.destination}, Номер рейса: {flight.flight_number}")
    else:
        print("Рейсы с указанным типом самолета не найдены")


def main() -> None:
    parser = argparse.ArgumentParser(description='Manage flight data')
    parser.add_argument('--input', action='store_true', help='Input new flight data')
    parser.add_argument('--print_plane_type', action='store_true', help='Print flights with specific plane type')
    args = parser.parse_args()

    home_dir = Path.home()
    data_file = home_dir / "flights.xml"
    schedule = FlightSchedule()

    if args.input:
        input_flights(schedule)
    else:
        schedule.load_from_xml(data_file)

    if args.print_plane_type:
        print_flights_with_plane_type(schedule)

    schedule.save_to_xml(data_file)


if __name__ == "__main__":
    main()
