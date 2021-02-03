Set-StrictMode -Version "4.0"

class MatrixConfig {
    [PSCustomObject]$displayNames
    [Hashtable]$displayNamesLookup
    [PSCustomObject]$import
    [PSCustomObject]$matrix
    [System.Collections.Specialized.OrderedDictionary]$orderedMatrix
    [Array]$include
    [Array]$exclude
}

$ALL_OF_KEYWORD = '$allOf'

function CreateDisplayName([string]$parameter, [Hashtable]$displayNamesLookup)
{
    $name = $parameter.ToString()

    if ($displayNamesLookup.ContainsKey($parameter)) {
        $name = $displayNamesLookup[$parameter]
    }

    # Matrix naming restrictions:
    # https://docs.microsoft.com/en-us/azure/devops/pipelines/process/phases?view=azure-devops&tabs=yaml#multi-job-configuration
    $name = $name -replace "[^A-Za-z0-9_]", ""
    return $name
}

function GenerateMatrix(
    [MatrixConfig]$config,
    [string]$selectFromMatrixType,
    [string]$displayNameFilter = ".*",
    [array]$filters = @()
) {
    $import = $null
    if ($config.import -and ($config.import.combineWith -eq "matrix" -or $config.import.combineWith -eq "all") {
        $import = $config.import
    }

    if ($selectFromMatrixType -eq "sparse") {
        [Array]$matrix = GenerateSparseMatrix $config.orderedMatrix $config.displayNamesLookup $import
    } elseif ($selectFromMatrixType -eq "all") {
        [Array]$matrix = GenerateFullMatrix $config.orderedMatrix $config.displayNamesLookup $import
    } else {
        throw "Matrix generator not implemented for selectFromMatrixType: $($platform.selectFromMatrixType)"
    }

    if ($config.exclude) {
        [Array]$matrix = ProcessExcludes $matrix $config.exclude
    }
    if ($config.include) {
        [Array]$matrix = ProcessIncludes $config $matrix
    }

    [Array]$matrix = FilterMatrixDisplayName $matrix $displayNameFilter
    [Array]$matrix = FilterMatrix $matrix $filters
    return $matrix
}

function FilterMatrixDisplayName([array]$matrix, [string]$filter) {
    return $matrix | ForEach-Object {
        if ($_.Name -match $filter) {
            return $_
        }
    }
}

# Filters take the format of key=valueregex,key2=valueregex2
function FilterMatrix([array]$matrix, [array]$filters) {
    $matrix = $matrix | ForEach-Object {
        if (MatchesFilters $_ $filters) {
            return $_
        }
    }
    return $matrix
}

function MatchesFilters([hashtable]$entry, [array]$filters) {
    foreach ($filter in $filters) {
        $key, $regex = ParseFilter $filter
        # Default all regex checks to go against empty string when keys are missing.
        # This simplifies the filter syntax/interface to be regex only.
        $value = ""
        if ($null -ne $entry -and $entry.parameters.Contains($key)) {
            $value = $entry.parameters[$key]
        }
        if ($value -notmatch $regex) {
            return $false
        }
    }

    return $true
}

function ParseFilter([string]$filter) {
    # Lazy match key in case value contains '='
    if ($filter -match "(.+?)=(.+)") {
        $key = $matches[1]
        $regex = $matches[2]
        return $key, $regex
    } else {
        throw "Invalid filter: `"${filter}`", expected <key>=<regex> format"
    }
}

# Importing the JSON as PSCustomObject preserves key ordering,
# whereas ConvertFrom-Json -AsHashtable does not
function GetMatrixConfigFromJson($jsonConfig)
{
    [MatrixConfig]$config = $jsonConfig | ConvertFrom-Json
    $config.orderedMatrix = [ordered]@{}
    $config.displayNamesLookup = @{}

    if ($null -ne $config.matrix) {
        $config.matrix.PSObject.Properties | ForEach-Object {
            $config.orderedMatrix.Add($_.Name, $_.Value)
        }
    }
    if ($null -ne $config.displayNames) {
        $config.displayNames.PSObject.Properties | ForEach-Object {
            $config.displayNamesLookup.Add($_.Name, $_.Value)
        }
    }
    if ($null -ne $config.import) {
        $config.import.selection = $config.selection
    }
    $config.include = $config.include | Where-Object { $null -ne $_ } | ForEach-Object {
        $ordered = [ordered]@{}
        $_.PSObject.Properties | ForEach-Object {
            $ordered.Add($_.Name, $_.Value)
        }
        return $ordered
    }
    $config.exclude = $config.exclude | Where-Object { $null -ne $_ } | ForEach-Object {
        $ordered = [ordered]@{}
        $_.PSObject.Properties | ForEach-Object {
            $ordered.Add($_.Name, $_.Value)
        }
        return $ordered
    }

    return $config
}

function ProcessExcludes([Array]$matrix, [Array]$excludes)
{
    $deleteKey = "%DELETE%"
    $exclusionMatrix = @()

    foreach ($exclusion in $excludes) {
        $full = GenerateFullMatrix $exclusion
        $exclusionMatrix += $full
    }

    foreach ($element in $matrix) {
        foreach ($exclusion in $exclusionMatrix) {
            $match = MatrixElementMatch $element.parameters $exclusion.parameters
            if ($match) {
                $element.parameters[$deleteKey] = $true
            }
        }
    }

    return $matrix | Where-Object { !$_.parameters.Contains($deleteKey) }
}

function ProcessIncludes([MatrixConfig]$config, [Array]$matrix) {
{
    $inclusionMatrix = @()
    foreach ($inclusion in $config.include) {
        $full = GenerateFullMatrix $inclusion $config.displayNamesLookup
        $inclusionMatrix += $full
    }
    if ($config.import -and ($config.import.combineWith -eq "include" -or $config.import.combineWith -eq "all") {
        $inclusionMatrix += ProcessImport $config $inclusionMatrix
    }

    $matrix += $inclusionMatrix

    return $matrix
}

function ProcessImport([PSCustomObject]$import, [Array]$matrix)
{
    if (-not $import) {
        return $matrix
    }

    $crossProductImported = @()
    $matrixConfig = GetMatrixConfigFromJson (Get-Content $import.path)
    $importedMatrix = GenerateMatrix $matrixConfig $import.selection

    foreach ($entry in $matrix) {
        foreach ($importedEntry in $importedMatrix) {
            $newEntry = @{
                name = $entry.name
                parameters = CloneOrderedDictionary($entry.parameters)
            }
            foreach($param in $importedEntry.parameters.GetEnumerator()) {
                if (-not $newEntry.Contains($param.Name)) {
                    $newEntry.parameters[$param.Name] = $param.Value
                } else {
                    Write-Warning "Skipping duplicate parameter `"$($param.Name)`" from imported matrix."
                }
            }

            # The maximum allowed matrix name length is 100 characters
            $newEntry.name = $newEntry.name, $importedEntry.name -join "_"
            if ($newEntry.name.Length -gt 100) {
                $newEntry.name = $newEntry.name[0..99] -join ""
            }

            $crossProductImported += $newEntry
        }
    }

    return $crossProductImported
}

function MatrixElementMatch([System.Collections.Specialized.OrderedDictionary]$source, [System.Collections.Specialized.OrderedDictionary]$target)
{
    if ($target.Count -eq 0) {
        return $false
    }

    foreach ($key in $target.Keys) {
        if (-not $source.Contains($key) -or $source[$key] -ne $target[$key]) {
            return $false
        }
    }

    return $true
}

function CloneOrderedDictionary([System.Collections.Specialized.OrderedDictionary]$dictionary) {
    $newDictionary = [Ordered]@{}
    foreach ($element in $dictionary.GetEnumerator()) {
        $newDictionary[$element.Name] = $element.Value
    }
    return $newDictionary
}

function SerializePipelineMatrix([Array]$matrix)
{
    $pipelineMatrix = [Ordered]@{}
    foreach ($entry in $matrix) {
        $pipelineMatrix.Add($entry.name, [Ordered]@{})
        foreach ($key in $entry.parameters.Keys) {
            $pipelineMatrix[$entry.name].Add($key, $entry.parameters[$key])
        }
    }

    return @{
        compressed = $pipelineMatrix | ConvertTo-Json -Compress ;
        pretty = $pipelineMatrix | ConvertTo-Json;
    }
}

function GenerateSparseMatrix(
    [System.Collections.Specialized.OrderedDictionary]$parameters,
    [Hashtable]$displayNamesLookup,
    [PSCustomObject]$import = $null
) {
    [Array]$dimensions = GetMatrixDimensions $parameters
    $size = ($dimensions | Measure-Object -Maximum).Maximum

    $processedParameters = @()
    foreach ($param in $parameters.GetEnumerator()) {
        if ($param.Name -ne $ALL_OF_KEYWORD) {
            foreach ($allParam in $param.GetEnumerator()) {
                $parameterArray += $param
            }
        } else {
            $parameterArray += $param
        }
    }

    [Array]$matrix = GenerateFullMatrix $processedParameters $displayNamesLookup
    $sparseMatrix = @()

    # With full matrix, retrieve items by doing diagonal lookups across the matrix N times.
    # For example, given a matrix with dimensions 4, 3, 3:
    # 0, 0, 0
    # 1, 1, 1
    # 2, 2, 2
    # 3, 0, 0 <- 3, 3, 3 wraps to 3, 0, 0 given the dimensions
    for ($i = 0; $i -lt $size; $i++) {
        $idx = @()
        for ($j = 0; $j -lt $dimensions.Length; $j++) {
            $idx += $i % $dimensions[$j]
        }
        $sparseMatrix += GetNdMatrixElement $idx $matrix $dimensions
    }

    # If there is a matrix import, then it should be combined with all permutations of the top level sparse matrix
    $sparseMatrix = ProcessImport $import $sparseMatrix
    return $sparseMatrix
}

function GenerateFullMatrix(
    [System.Collections.Specialized.OrderedDictionary] $parameters,
    [Hashtable]$displayNamesLookup = @{},
    [PSCustomObject]$import = $null
) {
    # Handle when the config does not have a matrix specified (e.g. only the include field is specified)
    if ($parameters.Count -eq 0) {
        return @()
    }

    $parameterArray = @()
    foreach ($param in $parameters.GetEnumerator()) {
        if ($param.Name -eq $ALL_OF_KEYWORD) {
            foreach ($allParam in $param.GetEnumerator()) {
                $parameterArray += $param
            }
        } else {
            $parameterArray += $param
        }
    }

    $matrix = [System.Collections.ArrayList]::new()
    InitializeMatrix $parameterArray $displayNamesLookup $matrix

    $matrix = ProcessImport $import $matrix.ToArray()
    return $matrix
}

function CreateMatrixEntry([System.Collections.Specialized.OrderedDictionary]$permutation, [Hashtable]$displayNamesLookup = @{})
{
    $names = @()
    $splattedParameters = [Ordered]@{}

    foreach ($entry in $permutation.GetEnumerator()) {
        $nameSegment = ""

        if ($entry.Value -is [PSCustomObject]) {
            $nameSegment = CreateDisplayName $entry.Name $displayNamesLookup
            foreach ($toSplat in $entry.Value.PSObject.Properties) {
                $splattedParameters.Add($toSplat.Name, $toSplat.Value)
            }
        } else {
            $nameSegment = CreateDisplayName $entry.Value $displayNamesLookup
            $splattedParameters.Add($entry.Name, $entry.Value)
        }

        if ($nameSegment) {
            $names += $nameSegment
        }
    }

    # The maximum allowed matrix name length is 100 characters
    $name = $names -join "_"
    if ($name.Length -gt 100) {
        $name = $name[0..99] -join ""
    }
    $stripped = $name -replace "^[^A-Za-z]*", ""  # strip leading digits
    if ($stripped -eq "") {
        $name = "job_" + $name  # Handle names that consist entirely of numbers
    } else {
        $name = $stripped
    }

    return @{
        name = $name
        parameters = $splattedParameters
    }
}

function InitializeMatrix
{
    param(
        [Array]$parameters,
        [Hashtable]$displayNamesLookup,
        [System.Collections.ArrayList]$permutations,
        $permutation = [Ordered]@{}
    )
    $head, $tail = $parameters

    if (-not $head) {
        $entry = CreateMatrixEntry $permutation $displayNamesLookup
        $permutations.Add($entry) | Out-Null
        return
    }

    # This behavior implicitly treats non-array values as single elements
    foreach ($value in $head.Value) {
        $newPermutation = CloneOrderedDictionary($permutation)
        if ($value -is [PSCustomObject]) {
            foreach ($nestedParameter in $value.PSObject.Properties) {
                $nestedPermutation = CloneOrderedDictionary($newPermutation)
                $nestedPermutation[$nestedParameter.Name] = $nestedParameter.Value
                InitializeMatrix $tail $displayNamesLookup $permutations $nestedPermutation
            }
        } else {
            $newPermutation[$head.Name] = $value
            InitializeMatrix $tail $displayNamesLookup $permutations $newPermutation
        }
    }
}

function GetMatrixDimensions([System.Collections.Specialized.OrderedDictionary]$parameters)
{
    $dimensions = @()
    foreach ($param in $parameters.GetEnumerator()) {
        if ($param.Value -is [PSCustomObject]) {
            $dimensions += ($param.Value.PSObject.Properties | Measure-Object).Count
        } elseif ($param.Value -is [Array]) {
            $dimensions += $param.Value.Length
        } else {
            $dimensions += 1
        }
    }

    return $dimensions
}

function SetNdMatrixElement
{
    param(
        $element,
        [ValidateNotNullOrEmpty()]
        [Array]$idx,
        [ValidateNotNullOrEmpty()]
        [Array]$matrix,
        [ValidateNotNullOrEmpty()]
        [Array]$dimensions
    )

    if ($idx.Length -ne $dimensions.Length) {
        throw "Matrix index query $($idx.Length) must be the same length as its dimensions $($dimensions.Length)"
    }

    $arrayIndex = GetNdMatrixArrayIndex $idx $dimensions
    $matrix[$arrayIndex] = $element
}

function GetNdMatrixArrayIndex
{
    param(
        [ValidateNotNullOrEmpty()]
        [Array]$idx,
        [ValidateNotNullOrEmpty()]
        [Array]$dimensions
    )

    if ($idx.Length -ne $dimensions.Length) {
        throw "Matrix index query length ($($idx.Length)) must be the same as dimension length ($($dimensions.Length))"
    }

    $stride = 1
    # Commented out does lookup with wrap handling
    # $index = $idx[$idx.Length-1] % $dimensions[$idx.Length-1]
    $index = $idx[$idx.Length-1]

    for ($i = $dimensions.Length-1; $i -ge 1; $i--) {
        $stride *= $dimensions[$i]
        # Commented out does lookup with wrap handling
        # $index += ($idx[$i-1] % $dimensions[$i-1]) * $stride
        $index += $idx[$i-1] * $stride
    }

    return $index
}

function GetNdMatrixElement
{
    param(
        [ValidateNotNullOrEmpty()]
        [Array]$idx,
        [ValidateNotNullOrEmpty()]
        [Array]$matrix,
        [ValidateNotNullOrEmpty()]
        [Array]$dimensions
    )

    $arrayIndex = GetNdMatrixArrayIndex $idx $dimensions
    return $matrix[$arrayIndex]
}

function GetNdMatrixIndex
{
    param(
        [int]$index,
        [ValidateNotNullOrEmpty()]
        [Array]$dimensions
    )

    $matrixIndex = @()
    $stride = 1

    for ($i = $dimensions.Length-1; $i -ge 1; $i--) {
        $stride *= $dimensions[$i]
        $page = [math]::floor($index / $stride) % $dimensions[$i-1]
        $matrixIndex = ,$page + $matrixIndex
    }
    $col = $index % $dimensions[$dimensions.Length-1]
    $matrixIndex += $col

    return $matrixIndex
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# The below functions are non-dynamic examples that   #
# help explain the above N-dimensional algorithm      #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #
function Get4dMatrixElement([Array]$idx, [Array]$matrix, [Array]$dimensions)
{
    $stride1 = $idx[0] * $dimensions[1] * $dimensions[2] * $dimensions[3]
    $stride2 = $idx[1] * $dimensions[2] * $dimensions[3]
    $stride3 = $idx[2] * $dimensions[3]
    $stride4 = $idx[3]

    return $matrix[$stride1 + $stride2 + $stride3 + $stride4]
}

function Get4dMatrixIndex([int]$index, [Array]$dimensions)
{
    $stride1 = $dimensions[3]
    $stride2 = $dimensions[2]
    $stride3 = $dimensions[1]
    $page1 = [math]::floor($index / $stride1) % $dimensions[2]
    $page2 = [math]::floor($index / ($stride1 * $stride2)) % $dimensions[1]
    $page3 = [math]::floor($index / ($stride1 * $stride2 * $stride3)) % $dimensions[0]
    $remainder = $index % $dimensions[3]

    return @($page3, $page2, $page1, $remainder)
}

