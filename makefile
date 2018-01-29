install:
	install -d $(DESTDIR)/usr/share/isen/
	install -d $(DESTDIR)/usr/share/isen/planning-scrapper
	install -m 744 GetAllPlannings.py $(DESTDIR)/usr/share/isen/planning-scrapper/
	install -m 744 PlanningScrapper.py $(DESTDIR)/usr/share/isen/planning-scrapper/

remove:
	rm $(DESTDIR)/usr/share/isen/planning-scrapper/PlanningScrapper.py
	rm $(DESTDIR)/usr/share/isen/planning-scrapper/GetAllPlannings.py
	-rmdir $(DESTDIR)/usr/share/isen/planning-scrapper
	-rmdir $(DESTDIR)/usr/share/isen
