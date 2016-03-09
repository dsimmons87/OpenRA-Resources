from django.contrib import admin

from openra.models import Maps
from openra.models import Lints
from openra.models import Replays
from openra.models import Screenshots
from openra.models import Reports
from openra.models import Rating
from openra.models import ReplayPlayers
from openra.models import Comments
from openra.models import UnsubscribeComments

admin.site.register(Maps)
admin.site.register(Lints)
admin.site.register(Replays)
admin.site.register(ReplayPlayers)
admin.site.register(Screenshots)
admin.site.register(Reports)
admin.site.register(Rating)
admin.site.register(Comments)
admin.site.register(UnsubscribeComments)