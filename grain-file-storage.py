print("Running")

from inhabitants import inhabitant_1 as inhabitant

storage = inhabitant.GrainFileStorage()

storage.write("test.txt", "This is a small test")