# import form tests
from .forms.test_modelforms import BillFormTests
from .forms.test_forms import FormTests


# import model tests
from .models.test_depreciationbilldata import DepreciationBillDataTests
from .models.test_depreciationtaxation import DepreciationTaxationTests
from .models.test_depreciationtype import DepreciationTypeTests
from .models.test_electricbilldata import ElectricBillDataTests
from .models.test_mortgagebilldata import MortgageBillDataTests
from .models.test_mysunpowerhourlydata import MySunpowerHourlyDataTests
from .models.test_natgasbilldata import NatGasBillDataTests
from .models.test_realestate import RealEstateTests
from .models.test_realpropertyvalue import RealPropertyValueTests
from .models.test_serviceprovider import ServiceProviderTests
from .models.test_simplebilldata import SimpleBillDataTests
from .models.test_solarbilldata import SolarBillDataTests


# import view tests