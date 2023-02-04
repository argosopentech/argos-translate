1.8:
- Delete cached package files after they've been installed
- Automatically update packages to newer version with package.Package.update

1.7:
- Improved examples and documentation
- Use multiple links for redundancy and load balancing
- Add logger namespace
- CTranslate2 updates

1.6:
- [Argos Translate GUI](https://github.com/argosopentech/argos-translate-gui) to separate repo
- Bug fixes
- [File translation](https://github.com/dingedi/argos-translate-files)

1.5:
- Tag injection
- Upgrade to CTranslate2 2.0

1.4:
- Better support for seq2seq sentence boundary detection
- py2app support
- GPU support
- Improved logging
- CI testing
- Code formatting
- Consistently use pathlib.Path in package module instead of strings
- Broke backwards compatibility with package.Package.remove

1.3:
- argospm CLI tool
- CLI improvements
- Experimental sentence boundary detection using OpenNMT Seq2Seq model
- Removed requests dependency

1.2:
- Download packages from GUI
- Multiple hypotheses in translations
- Deprecated load_available_packages for get_available_packages
- Deprecated tranalsate.load_installed_languages for get_installed_languages
- Renamed cli to "argos-translate" and GUI executable to "argos-translate-gui"
- Broke backwards compatibility in translate.apply_packaged_translation
- Broke backwards compatibility in ITranslate.split_into_paragraphs

1.1:
- Automatic downloading and installation of packages (https://github.com/uav4geo/LibreTranslate/issues/30)
- Command Line Interface
(https://github.com/argosopentech/argos-translate/issues/3)
- XDG Compliance (https://github.com/uav4geo/LibreTranslate/issues/30)
- Stability improvements
- Emoji support/Replaced unknowns with source tokens 🚀
- Changed "length_penalty" to 0.2 (https://forum.opennmt.net/t/suggested-value-for-length-penalty/4134)
- P2P model distribution support

1.0:
Hello World
