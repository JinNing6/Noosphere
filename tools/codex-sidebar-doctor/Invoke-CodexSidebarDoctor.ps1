#requires -Version 7.2

[CmdletBinding()]
param(
    [Parameter()]
    [string]$StatePath = (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\.codex-global-state.json'),

    [Parameter()]
    [switch]$Json,

    [Parameter()]
    [string]$ExportEvidencePath,

    [Parameter()]
    [ValidateLength(1, 80)]
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9 ._()/:+-]{0,79}$')]
    [string]$CodexVersion,

    [Parameter()]
    [ValidateSet('project-groups', 'tasks-within-project', 'both', 'unsure')]
    [string]$ObservedScope,

    [Parameter()]
    [switch]$RepairLegacySingleLayer,

    [Parameter()]
    [switch]$SubmitPublicEvidence
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$toolName = 'codex-sidebar-doctor'
$toolVersion = '0.1.0'
$defaultStatePath = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\.codex-global-state.json'
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

if ($RepairLegacySingleLayer -and $SubmitPublicEvidence) {
    throw 'Repair and public evidence submission must be separate runs so the submitted report remains read-only.'
}
if ($Json -and $SubmitPublicEvidence) {
    throw 'Use the human-readable output when submitting so the created public Issue URL remains visible.'
}

function Get-JsonProperty {
    param(
        [AllowNull()]
        [object]$InputObject,
        [Parameter(Mandatory)]
        [string]$Name
    )

    if ($null -eq $InputObject) {
        return [pscustomobject]@{ Present = $false; Value = $null }
    }

    $property = $InputObject.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return [pscustomobject]@{ Present = $false; Value = $null }
    }

    return [pscustomobject]@{ Present = $true; Value = $property.Value }
}

function Get-ValueKind {
    param([AllowNull()][object]$Value)

    if ($null -eq $Value) { return 'null' }
    if ($Value -is [System.Array]) { return 'array' }
    if ($Value -is [System.Collections.IDictionary]) { return 'object' }
    if ($Value -is [pscustomobject]) { return 'object' }
    if ($Value -is [string]) { return 'string' }
    if ($Value -is [bool]) { return 'boolean' }
    return $Value.GetType().Name.ToLowerInvariant()
}

function Get-EntryCount {
    param([AllowNull()][object]$Value)

    if ($null -eq $Value) { return 0 }
    if ($Value -is [System.Array]) { return $Value.Count }
    if ($Value -is [System.Collections.IDictionary]) { return $Value.Count }
    if ($Value -is [pscustomobject]) { return @($Value.PSObject.Properties).Count }
    if ($Value -is [string]) {
        if ([string]::IsNullOrWhiteSpace($Value)) { return 0 }
        return 1
    }
    return 1
}

function Get-OperatingSystemName {
    if ([System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
            [System.Runtime.InteropServices.OSPlatform]::Windows)) {
        return 'windows'
    }
    if ([System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
            [System.Runtime.InteropServices.OSPlatform]::OSX)) {
        return 'macos'
    }
    if ([System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
            [System.Runtime.InteropServices.OSPlatform]::Linux)) {
        return 'linux'
    }
    return 'unknown'
}

function Resolve-FullPath {
    param([Parameter(Mandatory)][string]$Path)
    return [System.IO.Path]::GetFullPath($ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path))
}

function Test-SamePath {
    param(
        [Parameter(Mandatory)][string]$Left,
        [Parameter(Mandatory)][string]$Right
    )

    $comparison = if ((Get-OperatingSystemName) -eq 'windows') {
        [System.StringComparison]::OrdinalIgnoreCase
    } else {
        [System.StringComparison]::Ordinal
    }
    return [string]::Equals((Resolve-FullPath $Left), (Resolve-FullPath $Right), $comparison)
}

function Write-Utf8Json {
    param(
        [Parameter(Mandatory)][object]$Value,
        [Parameter(Mandatory)][string]$Path
    )

    $rendered = $Value | ConvertTo-Json -Depth 100
    [System.IO.File]::WriteAllText($Path, $rendered + [Environment]::NewLine, $utf8NoBom)
}

function Write-Result {
    param(
        [Parameter(Mandatory)][object]$Payload,
        [switch]$AsJson,
        [string]$EvidencePath
    )

    $rendered = $Payload | ConvertTo-Json -Depth 30

    if (-not [string]::IsNullOrWhiteSpace($EvidencePath)) {
        $resolvedEvidencePath = Resolve-FullPath $EvidencePath
        if (Test-SamePath -Left $resolvedEvidencePath -Right $StatePath) {
            throw 'Evidence output must not overwrite the Codex state file.'
        }
        if (Test-Path -LiteralPath $resolvedEvidencePath) {
            throw 'Evidence output already exists; choose a new file name.'
        }
        $evidenceParent = Split-Path -Parent $resolvedEvidencePath
        if (-not (Test-Path -LiteralPath $evidenceParent -PathType Container)) {
            throw 'Evidence output directory does not exist.'
        }
        [System.IO.File]::WriteAllText(
            $resolvedEvidencePath,
            $rendered + [Environment]::NewLine,
            $utf8NoBom
        )
    }

    if ($AsJson) {
        Write-Output $rendered
        return
    }

    Write-Output "Codex Sidebar Doctor $toolVersion"
    Write-Output "Result: $($Payload.diagnosis.classification)"
    Write-Output "View: $($Payload.diagnosis.mode) / $($Payload.diagnosis.project_sort_mode)"
    Write-Output "Top-level saved order entries: $($Payload.diagnosis.top_level_order_count)"
    Write-Output "Second ordering layer present: $($Payload.diagnosis.second_layer_present)"
    Write-Output "Repair: $($Payload.action.status)"
    Write-Output "Next step: $($Payload.next_step.message)"
    if (-not [string]::IsNullOrWhiteSpace($EvidencePath)) {
        Write-Output "Redacted evidence written to: $(Resolve-FullPath $EvidencePath)"
    }
}

$resolvedStatePath = Resolve-FullPath $StatePath
if (-not (Test-Path -LiteralPath $resolvedStatePath -PathType Leaf)) {
    throw "Codex state file was not found. Run the doctor on the machine where Codex Desktop is installed."
}

try {
    $stateText = [System.IO.File]::ReadAllText($resolvedStatePath)
    $state = $stateText | ConvertFrom-Json -Depth 100
} catch {
    throw 'Codex state exists but is not valid JSON. No changes were made.'
}

$topOrder = Get-JsonProperty -InputObject $state -Name 'project-order'
$atoms = Get-JsonProperty -InputObject $state -Name 'electron-persisted-atom-state'
$preferences = Get-JsonProperty -InputObject $atoms.Value -Name 'flat-project-sidebar-preferences-v1'
$modeProperty = Get-JsonProperty -InputObject $preferences.Value -Name 'mode'
$sortProperty = Get-JsonProperty -InputObject $preferences.Value -Name 'projectSortMode'
$secondOrder = Get-JsonProperty -InputObject $atoms.Value -Name 'unified-sidebar-project-order-v1'

$mode = if ($modeProperty.Present) { [string]$modeProperty.Value } else { $null }
$sortMode = if ($sortProperty.Present) { [string]$sortProperty.Value } else { $null }
$topOrderKind = if ($topOrder.Present) { Get-ValueKind $topOrder.Value } else { 'missing' }
$topOrderCount = if ($topOrder.Present) { Get-EntryCount $topOrder.Value } else { 0 }
$secondOrderKind = if ($secondOrder.Present) { Get-ValueKind $secondOrder.Value } else { 'missing' }
$secondOrderCount = if ($secondOrder.Present) { Get-EntryCount $secondOrder.Value } else { 0 }
$secondLayerPresent = $secondOrder.Present -and $secondOrderCount -gt 0

if (-not $preferences.Present -or -not $modeProperty.Present -or -not $sortProperty.Present) {
    $classification = 'unsupported-state-shape'
} elseif ($mode -ne 'project' -or $sortMode -ne 'updated_at') {
    $classification = 'not-applicable-sort-mode'
} elseif ($secondLayerPresent) {
    $classification = 'second-layer-present'
} elseif ($topOrder.Present -and $topOrderKind -ne 'array') {
    $classification = 'unsupported-state-shape'
} elseif ($topOrderCount -gt 0) {
    $classification = 'legacy-single-layer-match'
} else {
    $classification = 'no-persisted-project-order'
}

$osName = Get-OperatingSystemName
$isLiveState = Test-SamePath -Left $resolvedStatePath -Right $defaultStatePath
$codexProcessRunning = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ProcessName -in @('Codex', 'ChatGPT') }
).Count -gt 0

$repairBlockers = [System.Collections.Generic.List[string]]::new()
if ($classification -ne 'legacy-single-layer-match') {
    switch ($classification) {
        'second-layer-present' { $repairBlockers.Add('second-order-layer') }
        'not-applicable-sort-mode' { $repairBlockers.Add('recency-sort-not-selected') }
        'no-persisted-project-order' { $repairBlockers.Add('legacy-order-already-empty') }
        default { $repairBlockers.Add('unsupported-state-shape') }
    }
}
if ($isLiveState -and $osName -ne 'windows') {
    $repairBlockers.Add('live-repair-is-windows-only')
}
if ($isLiveState -and $codexProcessRunning) {
    $repairBlockers.Add('codex-running')
}
$repairSupported = $repairBlockers.Count -eq 0

switch ($classification) {
    'legacy-single-layer-match' {
        if ($repairSupported) {
            $nextStep = [ordered]@{
                kind = 'review-repair'
                message = 'The state matches the published Windows single-layer recovery. Review the backup boundary, fully stop Codex, then explicitly request repair.'
            }
        } else {
            $nextStep = [ordered]@{
                kind = 'stop-before-repair'
                message = 'The legacy state matches, but every listed repair blocker must be removed before any write.'
            }
        }
    }
    'second-layer-present' {
        $nextStep = [ordered]@{
            kind = 'collect-redacted-evidence'
            message = 'A newer ordering layer is present. Do not apply the legacy repair; export this redacted diagnosis for the cross-platform update.'
        }
    }
    'no-persisted-project-order' {
        $nextStep = [ordered]@{
            kind = 'collect-redacted-evidence'
            message = 'The published top-level repair does not apply. Investigate task recency, project assignment, or sidebar render/cache ordering.'
        }
    }
    'not-applicable-sort-mode' {
        $nextStep = [ordered]@{
            kind = 'no-action'
            message = 'Project recency sorting is not selected, so this diagnostic does not treat the current order as the published bug.'
        }
    }
    default {
        $nextStep = [ordered]@{
            kind = 'collect-redacted-evidence'
            message = 'The state schema is outside the published recovery boundary. Do not modify it with the legacy repair.'
        }
    }
}

$action = [ordered]@{
    requested = [bool]$RepairLegacySingleLayer
    status = 'not-requested'
    backup_created = $false
    post_repair_classification = $null
}

$payload = [ordered]@{
    schema_version = 1
    record_kind = 'codex-sidebar-diagnostic'
    generated_at = [DateTimeOffset]::UtcNow.ToString('o')
    tool = [ordered]@{
        name = $toolName
        version = $toolVersion
        published_recovery = 'codex-project-recency-sort-recovery@1.0.0'
    }
    environment = [ordered]@{
        os = $osName
        powershell_version = $PSVersionTable.PSVersion.ToString()
        codex_version = if ([string]::IsNullOrWhiteSpace($CodexVersion)) { $null } else { $CodexVersion }
        live_state = $isLiveState
        codex_process_running = $codexProcessRunning
    }
    observation = [ordered]@{
        stale_ordering_observed = -not [string]::IsNullOrWhiteSpace($ObservedScope)
        scope = if ([string]::IsNullOrWhiteSpace($ObservedScope)) { $null } else { $ObservedScope }
    }
    diagnosis = [ordered]@{
        classification = $classification
        mode = $mode
        project_sort_mode = $sortMode
        top_level_order_present = $topOrder.Present
        top_level_order_kind = $topOrderKind
        top_level_order_count = $topOrderCount
        second_layer_present = $secondLayerPresent
        second_layer_kind = $secondOrderKind
        second_layer_count = $secondOrderCount
        repair_supported = $repairSupported
        repair_blockers = @($repairBlockers)
    }
    action = $action
    next_step = $nextStep
    privacy = [ordered]@{
        contains_project_names = $false
        contains_project_paths = $false
        contains_thread_ids = $false
        contains_conversation_content = $false
        contains_ordered_identifiers = $false
    }
    upstream = [ordered]@{
        primary_issue = 'https://github.com/openai/codex/issues/31836'
        related_activity_issue = 'https://github.com/openai/codex/issues/36300'
        related_task_issue = 'https://github.com/openai/codex/issues/35090'
    }
}

if ($RepairLegacySingleLayer) {
    if (-not $repairSupported) {
        $action.status = 'refused'
        Write-Result -Payload $payload -AsJson:$Json -EvidencePath $ExportEvidencePath
        exit 3
    }

    $stateItem = Get-Item -LiteralPath $resolvedStatePath -Force
    $timestamp = [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $token = [Guid]::NewGuid().ToString('N').Substring(0, 8)
    $backupPath = Join-Path $stateItem.DirectoryName "$($stateItem.Name).backup-$timestamp-$token.json"
    $temporaryPath = Join-Path $stateItem.DirectoryName ".$($stateItem.Name).tmp-$token"

    Copy-Item -LiteralPath $resolvedStatePath -Destination $backupPath -ErrorAction Stop
    $action.backup_created = $true

    try {
        $state.'project-order' = @()
        Write-Utf8Json -Value $state -Path $temporaryPath

        $verified = [System.IO.File]::ReadAllText($temporaryPath) | ConvertFrom-Json -Depth 100
        $verifiedTopOrder = Get-JsonProperty -InputObject $verified -Name 'project-order'
        $verifiedAtoms = Get-JsonProperty -InputObject $verified -Name 'electron-persisted-atom-state'
        $verifiedPreferences = Get-JsonProperty -InputObject $verifiedAtoms.Value -Name 'flat-project-sidebar-preferences-v1'
        $verifiedMode = Get-JsonProperty -InputObject $verifiedPreferences.Value -Name 'mode'
        $verifiedSort = Get-JsonProperty -InputObject $verifiedPreferences.Value -Name 'projectSortMode'

        if (-not $verifiedTopOrder.Present -or
            (Get-ValueKind $verifiedTopOrder.Value) -ne 'array' -or
            (Get-EntryCount $verifiedTopOrder.Value) -ne 0 -or
            [string]$verifiedMode.Value -ne 'project' -or
            [string]$verifiedSort.Value -ne 'updated_at') {
            throw 'Temporary state validation failed.'
        }

        [System.IO.File]::Move($temporaryPath, $resolvedStatePath, $true)
        $action.status = 'applied'
        $action.post_repair_classification = 'no-persisted-project-order'
    } catch {
        if (Test-Path -LiteralPath $temporaryPath) {
            Remove-Item -LiteralPath $temporaryPath -Force
        }
        Copy-Item -LiteralPath $backupPath -Destination $resolvedStatePath -Force
        $action.status = 'rolled-back'
        throw 'Repair failed validation and the original state was restored from backup.'
    }
}

Write-Result -Payload $payload -AsJson:$Json -EvidencePath $ExportEvidencePath

if ($SubmitPublicEvidence) {
    if (-not $isLiveState) {
        throw 'Public evidence submission accepts the live Codex state only, not a copied fixture.'
    }
    if ([string]::IsNullOrWhiteSpace($CodexVersion)) {
        throw 'CodexVersion is required before public submission.'
    }
    if ([string]::IsNullOrWhiteSpace($ObservedScope)) {
        throw 'ObservedScope is required before public submission so project-group and task-level failures remain separate.'
    }
    if ($classification -eq 'not-applicable-sort-mode') {
        throw 'The current settings do not reproduce the recency-sort condition, so no public diagnostic was submitted.'
    }
    $ghCommand = Get-Command gh -ErrorAction SilentlyContinue
    if ($null -eq $ghCommand) {
        throw 'GitHub CLI is required for one-command submission. Export the JSON and use the Issue Form instead.'
    }
    & $ghCommand.Source auth status *> $null
    if ($LASTEXITCODE -ne 0) {
        throw 'GitHub CLI is not authenticated. Run gh auth login, then retry the explicit submission command.'
    }

    $reportJson = $payload | ConvertTo-Json -Depth 30
    $issueBody = @(
        '### Generated sidebar diagnostic JSON'
        ''
        '```json'
        $reportJson
        '```'
        ''
        '### Public submission declaration'
        ''
        '- [x] I personally observed stale Codex sidebar ordering in the scope recorded by this live-state report.'
        '- [x] I reviewed the generated report and it contains no project names, paths, task identifiers, or conversation content.'
        '- [x] I consent to automatic validation and public storage under my authenticated GitHub identity.'
    ) -join [Environment]::NewLine
    $issueTitle = "Codex sidebar diagnostic: $classification ($osName)"
    $submissionUrl = & $ghCommand.Source issue create `
        --repo 'JinNing6/Noosphere' `
        --title $issueTitle `
        --body $issueBody
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($submissionUrl)) {
        throw 'GitHub did not confirm creation of the public diagnostic Issue.'
    }
    Write-Output "Public diagnostic submitted: $($submissionUrl.Trim())"
}
