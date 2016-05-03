# (C) 2016 Elke Schaper

from hts.plate_data.plate_data import PlateData

class MetaData(PlateData):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tags.append("meta")