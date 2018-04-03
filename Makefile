update:
	./updatefromreport.sh

generate:
	./generate.py --parallel --calendar

upload:
	./upload.sh

.PHONY: update generate upload

