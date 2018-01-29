install:
	@echo "Installing scripts"
	install -D -m 744 GetAllPlannings.py $(DESTDIR)/usr/share/isen/planning-scrapper/
	install -D -m 744 PlanningScrapper.py $(DESTDIR)/usr/share/isen/planning-scrapper/

	@echo "Installing systemd files"
	install -D -m 644 isen-plannings.service $(DESTDIR)/usr/lib/systemd/system/isen-plannings.service
	install -D -m 644 isen-plannings.timer $(DESTDIR)/usr/lib/systemd/system/isen-plannings.timer

remove:
	@echo "Removing systemd files"
	rm $(DESTDIR)/usr/lib/systemd/system/isen-plannings.timer
	rm $(DESTDIR)/usr/lib/systemd/system/isen-plannings.service

	@echo "Removing scripts"
	rm $(DESTDIR)/usr/share/isen/planning-scrapper/PlanningScrapper.py
	rm $(DESTDIR)/usr/share/isen/planning-scrapper/GetAllPlannings.py

	@echo "Removing empty folders"
	-rmdir $(DESTDIR)/usr/share/isen/planning-scrapper
	-rmdir $(DESTDIR)/usr/share/isen
