from frozendict import frozendict
contest_json = frozendict({
    "__type": "problemWithChecker",
    "id": "30404/2016_09_03/cxn5ayBEb8",
    "ownerId": 404,
    "testFileType": "text",
    "creationTime": 1472915818089,
    "modifyTime": 1473535609432,
    "shortName": "",
    "defaultLocale": "ru",
    "names": {
        "ru": "",
        "en": ""
    },
    "statements": [{
        "locale": "ru",
        "type": "tex",
        "path": "statements/.html/ru/texstatement.html",
        "additional": False,
        "auxiliaryFiles": [],
        "state": "valid",
        "rendered": False,
        "texStatement": {
            "legend": "",
            "inputFormat": "",
            "outputFormat": "",
            "notes": ""
        }
    }],
    "fileSet": {
        "inputFile": "input.txt",
        "outputFile": "output.txt",
        "redirectStdin": True,
        "redirectStdout": True
    },
    "solutionLimits": {
        "timeLimitMillis": 1000,
        "idlenessLimitMillis": 10000,
        "memoryLimit": 67108864,
        "outputLimit": 67108864
    },
    "deleted": False,
    "sourceSizeLimit": 262144,
    "fileCreationAllowed": False,
    "customCompilerGroupLimits": [],
    "testSets": [{
        "name": "samples",
        "inputFilePattern": "tests/{01-03}",
        "answerFilePattern": "*.a",
        "matchedTests": [],
        "testsMatched": False
    }, {
        "name": "All tests",
        "inputFilePattern": "tests/{01-}",
        "answerFilePattern": "*.a",
        "matchedTests": [],
        "testsMatched": False
    }],
    "generators": [],
    "generateTestCommands": [],
    "solutions": [{
        "compilerId": "",
        "sourcePath": "",
        "verdict": "ok"
    }],
    "tags": [],
    "includeFiles": [],
    "includeRunFiles": [],
    "postProcessFiles": [],
    "validators": [],
    "htmlGenerator": "ya-contest",
    "compilationLimits": {
        "timeLimitMillis": 60000,
        "idlenessLimitMillis": 60000,
        "memoryLimit": 1598029824,
        "outputLimit": 100000000
    },
    "customCompilationLimits": [],
    "fieldType": "text-or-file",
    "validation": {},
    "userAccess": [],
    "checkerSettings": {
        "__type": "standardChecker",
        "limits": {
            "timeLimitMillis": 10000,
            "idlenessLimitMillis": 10000,
            "memoryLimit": 268435456,
            "outputLimit": 268435456
        },
        "env": {},
        "checkerId": "wcmp"
    }
})
