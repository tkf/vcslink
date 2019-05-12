.PHONY: inject-readme check-readme

## Inject content of README.rst to the top-level docstring.
inject-readme: $(TOPMODULE)
$(TOPMODULE): README.rst
	sed -E -e '0,/^r?"""$$/d' -e '0,/^"""$$/d' $@ > $@.tail
	rm $@
	echo 'r"""' >> $@
	cat README.rst >> $@
	echo '"""' >> $@
	cat $@.tail >> $@
	rm $@.tail

# Check that README.rst and $(TOPMODULE) are in the consistent state.
check-readme:
	git status --short --untracked-files=no | xargs --no-run-if-empty false
	$(MAKE) --always-make inject-readme
	git status --short --untracked-files=no | xargs --no-run-if-empty false
