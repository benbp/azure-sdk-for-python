Import-Module Pester

BeforeAll {
    . ./job-matrix-functions.ps1
}

Describe "Platform Matrix Import" -Tag "import" {
    BeforeEach {
        $matrixConfigForObject = @'
{
    "matrix": {
        "testField": [ "test1", "test2" ],
        "$IMPORT": {
            "path": "./test-import-matrix.json",
            "selection": "all"
        }
    },
    "include": [
      {
        "testImportInclude": {
            "testImportIncludeName": { "testValue1": "1", "testValue2": "2" }
        }
      }
    ],
    "exclude": [
      {
        "Foo": 1,
        "Bar": [ "a", "b" ]
      }
    ]
}
'@

        $importConfig = GetMatrixConfigFromJson $matrixConfigForObject
    }

    It "Should generate a full matrix with an imported sparse matrix" {
        $matrixJson = @'
{
    "matrix": {
        "testField": [ "test1", "test2" ],
        "$IMPORT": {
            "path": "./test-import-matrix.json",
            "selection": "sparse"
        }
    }
}
'@
        $importConfig = GetMatrixConfigFromJson $matrixJson
        $matrix = GenerateMatrix $importConfig "all"

        $matrix.Length | Should -Be 6

        $matrix[0].name | Should -Be test1_foo1_bar1
        $matrix[0].parameters.testField | Should -Be "test1"
        $matrix[0].parameters.Foo | Should -Be "foo1"
        $matrix[2].name | Should -Be test1_includedBaz
        $matrix[2].parameters.testField | Should -Be "test1"
        $matrix[2].parameters.Baz | Should -Be "includedBaz"
        $matrix[4].name | Should -Be test2_foo2_bar2
        $matrix[4].parameters.testField | Should -Be "test2"
        $matrix[4].parameters.Foo | Should -Be "foo2"
    }

    It "Should generate a sparse matrix with an imported a sparse matrix" {
        $matrixJson = @'
{
    "matrix": {
        "testField1": [ "test11", "test12" ],
        "testField2": [ "test21", "test22" ],
        "$IMPORT": {
            "path": "./test-import-matrix.json",
            "selection": "sparse"
        }
    }
}
'@
        $importConfig = GetMatrixConfigFromJson $matrixJson
        $matrix = GenerateMatrix $importConfig "sparse"

        $matrix.Length | Should -Be 6

        $matrix[0].name | Should -Be test11_test21_foo1_bar1
        $matrix[0].parameters.testField1 | Should -Be "test11"
        $matrix[0].parameters.testField2 | Should -Be "test21"
        $matrix[0].parameters.Foo | Should -Be "foo1"
        $matrix[2].name | Should -Be test11_test21_includedBaz
        $matrix[2].parameters.testField1 | Should -Be "test11"
        $matrix[2].parameters.testField2 | Should -Be "test21"
        $matrix[2].parameters.Baz | Should -Be "includedBaz"
        $matrix[4].name | Should -Be test12_test22_foo2_bar2
        $matrix[4].parameters.testField1 | Should -Be "test12"
        $matrix[4].parameters.testField2 | Should -Be "test22"
        $matrix[4].parameters.Foo | Should -Be "foo2"
    }

    It "Should get matrix dimensions with an import" {
        [Array]$dimensions = GetMatrixDimensions $importConfig.orderedMatrix
        $dimensions | Should -Be @(2)
    }
}
