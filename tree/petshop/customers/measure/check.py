#!/usr/bin/env python3
"""Measure of customers. Usage: check.py UNIT_DIR (the folder holding work/customers.py).
Invented names only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "measure"))
from scenarios import main, refuses, scenario, through_json



def shop(m):
    c = m.Customers({})
    ana = c.add_customer("Ana Souza", "555-0101")
    return c, ana, c.add_pet(ana, "Rex", "dog")


@scenario
def add_customer(m):
    """a customer is added and read back with name and phone"""
    c, ana, _ = shop(m)
    assert c.customer(ana) == {"id": ana, "name": "Ana Souza", "phone": "555-0101"}


@scenario
def ids_differ(m):
    """each customer and each pet gets its own id"""
    c, ana, rex = shop(m)
    bia = c.add_customer("Bia Lima", "555-0102")
    assert bia != ana and c.add_pet(bia, "Mia", "cat") != rex


@scenario
def name_required(m):
    """a customer or a pet with no name is refused and nothing is stored"""
    c, ana, _ = shop(m)
    refuses(ValueError, c.add_customer, "", "555")
    refuses(ValueError, c.add_customer, "   ", "555")
    refuses(ValueError, c.add_pet, ana, " ", "dog")
    assert len(c.find("")) == 1 and len(c.pets_of(ana)) == 1


@scenario
def add_pet(m):
    """a pet belongs to its customer"""
    c, ana, rex = shop(m)
    assert c.pet(rex) == {"id": rex, "customer_id": ana, "name": "Rex", "species": "dog"}
    assert c.pets_of(ana) == [c.pet(rex)]


@scenario
def pet_needs_customer(m):
    """a pet for an unknown customer is refused"""
    c, _, _ = shop(m)
    refuses(LookupError, c.add_pet, 999, "Mia", "cat")


@scenario
def unknown(m):
    """asking for a customer or pet that does not exist is refused, not answered empty"""
    c, _, _ = shop(m)
    refuses(LookupError, c.customer, 999)
    refuses(LookupError, c.pet, 999)
    refuses(LookupError, c.pets_of, 999)


@scenario
def no_pets(m):
    """a customer with no pets has an empty list"""
    c, _, _ = shop(m)
    assert c.pets_of(c.add_customer("Bia Lima", "555-0102")) == []


@scenario
def find(m):
    """the staff find a customer by part of the name, of the phone or of a pet's name, in any case"""
    c, ana, _ = shop(m)
    bia = c.add_customer("Bia Lima", "555-0102")
    ids = lambda text: sorted(x["id"] for x in c.find(text))
    assert ids("souza") == [ana] and ids("0102") == [bia] and ids("REX") == [ana]
    assert ids("") == sorted([ana, bia]) and ids("zzz") == []


@scenario
def known(m):
    """has_customer and has_pet answer yes or no, for the other areas"""
    c, ana, rex = shop(m)
    assert c.has_customer(ana) is True and c.has_customer(999) is False
    assert c.has_pet(rex) is True and c.has_pet(999) is False


@scenario
def update(m):
    """name and phone can be corrected, one or both; a blank name is refused"""
    c, ana, _ = shop(m)
    c.update_customer(ana, phone="555-0199")
    assert c.customer(ana) == {"id": ana, "name": "Ana Souza", "phone": "555-0199"}
    c.update_customer(ana, name="Ana S. Souza")
    assert c.customer(ana)["name"] == "Ana S. Souza" and c.customer(ana)["phone"] == "555-0199"
    refuses(ValueError, c.update_customer, ana, name=" ")
    refuses(LookupError, c.update_customer, 999, phone="1")


@scenario
def copies(m):
    """what is read is a copy: changing it does not change the shop"""
    c, ana, rex = shop(m)
    c.customer(ana)["name"] = "x"
    c.pet(rex)["name"] = "x"
    c.pets_of(ana).clear()
    assert c.customer(ana)["name"] == "Ana Souza" and c.pet(rex)["name"] == "Rex" and len(c.pets_of(ana)) == 1


@scenario
def state_is_data(m):
    """everything lives in the state it was given, which survives being written as JSON"""
    state = {}
    c = m.Customers(state)
    ana = c.add_customer("Ana Souza", "555-0101")
    rex = c.add_pet(ana, "Rex", "dog")
    again = m.Customers(through_json(state))
    assert again.customer(ana)["name"] == "Ana Souza" and again.pet(rex)["customer_id"] == ana
    assert again.add_customer("Bia Lima", "555-0102") != ana and again.add_pet(ana, "Mia", "cat") != rex


@scenario
def ids_are_numbers(m):
    """an id written as text is not an id: it is not found, and nothing is stored under it"""
    c, ana, rex = shop(m)
    refuses(LookupError, c.add_pet, str(ana), "Mia", "cat")
    refuses(LookupError, c.customer, str(ana))
    refuses(LookupError, c.pet, str(rex))
    refuses(LookupError, c.pets_of, str(ana))
    refuses(LookupError, c.update_customer, str(ana), phone="1")
    assert c.has_customer(str(ana)) is False and c.has_pet(str(rex)) is False
    assert c.has_customer(float(ana)) is False and c.has_pet(None) is False
    assert len(c.pets_of(ana)) == 1 and c.customer(ana)["phone"] == "555-0101"


if __name__ == "__main__":
    main("customers", expected=13)
