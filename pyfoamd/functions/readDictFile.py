def readDictFile(file):

    #from of.ofTypes import ofDictFile, ofDict, ofNamedList, ofIntValue, ofFloatValue, ofStrValue

    #- Function assumes:
    #   - All entries start on a new line
    #   - Comments on line after C++ code are ignored

    pyOFDict = ofDictFile(os.path.basename(file), [])

    def functionSwitcher(status):
        switcher = {
            'commentedBlock': _getOFDictCommentLineType,
            'comment': None,
            'includeLine': None,
            'empty': None,
            'commentedBlockEnd':  _getOFDictReadLineType,
            'list': _getOFDictValueType,
            'dict': _getOFDictValueType,
            'value': _storeOFDictValue,
            'multiLineUnknown': _getOFDictEntryType,
            'dictName': _newOFDictDict,
            'listName': _newOFDictList,
            'multiLineValue': _appendOFDictEntry,
            'multiLineEntryStart': _storeOFDictMultiLineEntryName,
            'singleLineSingleValuedEntry': _storeOFDictSingleLineSingleValuedEntry
        }
        return switcher.get(status, _getOFDictReadLineType)
