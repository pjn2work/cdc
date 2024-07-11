from testipy.helpers.data_driven_testing import DDTMethods
from testipy.reporter import ReportManager

from toolbox import Toolbox


class SuitePopulate:
    """
    @LEVEL 1
    @TAG DDT INIT
    """

    def __init__(self):
        self.ddt = DDTMethods("populate.yaml", env_name="", exec_toolbox=Toolbox())

    def test_setup(self, ma: dict, rm: ReportManager, **kwargs):
        """
        @LEVEL 2
        @PRIO 0
        """
        self.ddt.run(ma, rm, tag_name="SETUP")

    def test_populate(self, ma: dict, rm: ReportManager, **kwargs):
        """
        @ON_SUCCESS 0
        @LEVEL 2
        @PRIO 5
        """
        self.ddt.run(ma, rm, tag_name="POPULATE")
