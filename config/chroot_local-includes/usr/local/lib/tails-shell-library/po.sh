# This shell library is meant to be used with `set -e` and `set -u`.

po_languages () {
   for po in po/*.po ; do
      rel="${po%.po}"
      echo "${rel#po/}"
   done
}

intltool_update_po () {
   (
      cd po
      for locale in "$@" ; do
          intltool-update --dist --gettext-package=tails $locale -o ${locale}.po.new
      done
   )
}

keep_old_po_files_if_header_only_changed() {
    cd po
    for locale in "$@" ; do
         if [ ! -f ${locale}.po.new ]; then
             echo "New PO file for ${locale} does not exist. Skipping."
             continue
		else
             echo "${locale} PO file exists."
         fi
         if [ $(diff "${locale}.po" "${locale}.po.new" | grep ^"> " | wc -l) -eq 1 ]; then
             if diff -aw "${locale}.po" "${locale}.po.new" | grep ^'> "POT-Creation-Date:'; then
                 echo "Only header changes in potfile, Delete new PO file."
                 rm -f ${locale}.po.new
             fi
         else
             echo "Real changes in potfile: substitute old PO file."
             mv ${locale}.po.new ${locale}.po
         fi
    done
}
