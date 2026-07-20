param(
    [string]$Ffmpeg = "ffmpeg",
    [string]$Ffprobe = "ffprobe",
    [string]$Browser = ""
)

$ErrorActionPreference = "Stop"

if (-not ("NoosphereProcessJob" -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

public static class NoosphereProcessJob
{
    private const int JobObjectExtendedLimitInformation = 9;
    private const uint JobObjectLimitKillOnJobClose = 0x00002000;

    [StructLayout(LayoutKind.Sequential)]
    private struct BasicLimitInformation
    {
        public long PerProcessUserTimeLimit;
        public long PerJobUserTimeLimit;
        public uint LimitFlags;
        public UIntPtr MinimumWorkingSetSize;
        public UIntPtr MaximumWorkingSetSize;
        public uint ActiveProcessLimit;
        public UIntPtr Affinity;
        public uint PriorityClass;
        public uint SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct IoCounters
    {
        public ulong ReadOperationCount;
        public ulong WriteOperationCount;
        public ulong OtherOperationCount;
        public ulong ReadTransferCount;
        public ulong WriteTransferCount;
        public ulong OtherTransferCount;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct ExtendedLimitInformation
    {
        public BasicLimitInformation BasicLimitInformation;
        public IoCounters IoInfo;
        public UIntPtr ProcessMemoryLimit;
        public UIntPtr JobMemoryLimit;
        public UIntPtr PeakProcessMemoryUsed;
        public UIntPtr PeakJobMemoryUsed;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    private static extern IntPtr CreateJobObject(IntPtr attributes, string name);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetInformationJobObject(
        IntPtr job,
        int informationClass,
        IntPtr information,
        uint informationLength
    );

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);

    [DllImport("kernel32.dll")]
    private static extern bool CloseHandle(IntPtr handle);

    public static IntPtr CreateKillOnCloseJob()
    {
        IntPtr job = CreateJobObject(IntPtr.Zero, null);
        if (job == IntPtr.Zero)
            throw new Win32Exception(Marshal.GetLastWin32Error());

        var info = new ExtendedLimitInformation();
        info.BasicLimitInformation.LimitFlags = JobObjectLimitKillOnJobClose;
        int length = Marshal.SizeOf(typeof(ExtendedLimitInformation));
        IntPtr pointer = Marshal.AllocHGlobal(length);
        try
        {
            Marshal.StructureToPtr(info, pointer, false);
            if (!SetInformationJobObject(job, JobObjectExtendedLimitInformation, pointer, (uint)length))
                throw new Win32Exception(Marshal.GetLastWin32Error());
        }
        finally
        {
            Marshal.FreeHGlobal(pointer);
        }
        return job;
    }

    public static void Assign(IntPtr job, IntPtr process)
    {
        if (!AssignProcessToJobObject(job, process))
            throw new Win32Exception(Marshal.GetLastWin32Error());
    }

    public static void Close(IntPtr job)
    {
        if (job != IntPtr.Zero)
            CloseHandle(job);
    }
}
"@
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourcePath = Join-Path $PSScriptRoot "launch-assets\v090-live-skill.html"
$outputDir = Join-Path $repoRoot "assets\launch"
$socialPath = Join-Path $outputDir "noosphere-live-skills-v090-social-preview.png"
$mp4Path = Join-Path $outputDir "noosphere-live-skills-v090-demo.mp4"
$gifPath = Join-Path $outputDir "noosphere-live-skills-v090-demo.gif"

if (-not $Browser) {
    $browserCandidates = @(
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    )
    $Browser = $browserCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}

if (-not $Browser -or -not (Test-Path $Browser)) {
    throw "A Chromium browser is required. Pass -Browser with the Edge or Chrome executable."
}
if (-not (Test-Path $sourcePath)) {
    throw "Launch source not found: $sourcePath"
}

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("noosphere-v090-launch-" + [guid]::NewGuid())
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null
$jobHandle = [NoosphereProcessJob]::CreateKillOnCloseJob()

function Capture-Scene {
    param(
        [Parameter(Mandatory = $true)][string]$Query,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][string]$WindowSize
    )

    $uri = [System.Uri]::new($sourcePath).AbsoluteUri + $Query
    $profilePath = Join-Path $tempRoot "browser-profile"
    $stdoutPath = Join-Path $tempRoot ("browser-" + [guid]::NewGuid() + ".stdout.log")
    $stderrPath = Join-Path $tempRoot ("browser-" + [guid]::NewGuid() + ".stderr.log")
    $arguments = @(
        "--headless=new",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-extensions",
        "--disable-sync",
        "--hide-scrollbars",
        "--no-first-run",
        "--allow-file-access-from-files",
        "--user-data-dir=$profilePath",
        "--window-size=$WindowSize",
        "--screenshot=$Destination",
        $uri
    )
    $process = Start-Process -FilePath $Browser -ArgumentList $arguments -PassThru `
        -NoNewWindow -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    [NoosphereProcessJob]::Assign($jobHandle, $process.Handle)
    $process.WaitForExit()
    if ($process.ExitCode -ne 0 -or -not (Test-Path $Destination)) {
        throw "Browser capture failed: $Destination"
    }
}

try {
    Capture-Scene -Query "?mode=social" -Destination $socialPath -WindowSize "1280,640"

    $scenePaths = @()
    foreach ($scene in 1..5) {
        $scenePath = Join-Path $tempRoot ("scene-{0}.png" -f $scene)
        Capture-Scene -Query ("?mode=demo&scene={0}" -f $scene) -Destination $scenePath -WindowSize "1280,720"
        $scenePaths += $scenePath
    }

    $filter = @"
[0:v]fps=24,format=yuv420p[v0];
[1:v]fps=24,format=yuv420p[v1];
[2:v]fps=24,format=yuv420p[v2];
[3:v]fps=24,format=yuv420p[v3];
[4:v]fps=24,format=yuv420p[v4];
[v0][v1]xfade=transition=fade:duration=0.25:offset=2.95[x1];
[x1][v2]xfade=transition=fade:duration=0.25:offset=6.50[x2];
[x2][v3]xfade=transition=fade:duration=0.25:offset=10.25[x3];
[x3][v4]xfade=transition=fade:duration=0.25:offset=14.80[out]
"@ -replace "(`r`n|`n|`r)", ""

    & $Ffmpeg -y `
        -loop 1 -t 3.2 -i $scenePaths[0] `
        -loop 1 -t 3.8 -i $scenePaths[1] `
        -loop 1 -t 4.0 -i $scenePaths[2] `
        -loop 1 -t 4.8 -i $scenePaths[3] `
        -loop 1 -t 4.2 -i $scenePaths[4] `
        -filter_complex $filter -map "[out]" `
        -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart $mp4Path
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed while rendering the MP4" }

    $palettePath = Join-Path $tempRoot "palette.png"
    & $Ffmpeg -y -i $mp4Path `
        -vf "fps=10,scale=960:-1:flags=lanczos,palettegen=max_colors=96:stats_mode=diff" `
        -frames:v 1 -update 1 `
        $palettePath
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed while generating the GIF palette" }

    & $Ffmpeg -y -i $mp4Path -i $palettePath `
        -lavfi "fps=10,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle" `
        -loop 0 $gifPath
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed while rendering the GIF" }

    $socialBytes = (Get-Item $socialPath).Length
    if ($socialBytes -ge 1MB) {
        throw "Social preview must remain below GitHub's 1 MB limit: $socialBytes bytes"
    }

    Write-Output "Rendered $socialPath"
    Write-Output "Rendered $mp4Path"
    Write-Output "Rendered $gifPath"
    & $Ffprobe -v error -show_entries format=duration,size `
        -show_entries stream=width,height,r_frame_rate -of json $mp4Path
}
finally {
    [NoosphereProcessJob]::Close($jobHandle)
    $resolvedTemp = [System.IO.Path]::GetFullPath($tempRoot)
    $resolvedBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
    if ($resolvedTemp.StartsWith($resolvedBase, [System.StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
