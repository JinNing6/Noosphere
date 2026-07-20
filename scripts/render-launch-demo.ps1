param(
    [string]$Ffmpeg = "ffmpeg"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$outputDir = Join-Path $repoRoot "assets\demo"
$mp4Path = Join-Path $outputDir "agent-debug-memory.mp4"
$gifPath = Join-Path $outputDir "agent-debug-memory.gif"
$filterPath = Join-Path ([System.IO.Path]::GetTempPath()) ("noosphere-demo-" + [guid]::NewGuid() + ".filter")
$palettePath = Join-Path ([System.IO.Path]::GetTempPath()) ("noosphere-palette-" + [guid]::NewGuid() + ".png")

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$filter = @'
[0:v]
drawbox=x=0:y=0:w=iw:h=ih:color=0x07090f:t=fill,
drawbox=x=42:y=34:w=876:h=472:color=0x0d111a:t=fill,
drawbox=x=42:y=34:w=876:h=54:color=0x171c28:t=fill,
drawbox=x=66:y=58:w=10:h=10:color=0xff5f57:t=fill,
drawbox=x=84:y=58:w=10:h=10:color=0xfebc2e:t=fill,
drawbox=x=102:y=58:w=10:h=10:color=0x28c840:t=fill,
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='NOOSPHERE  /  AGENT DEBUG MEMORY':x=142:y=51:fontsize=20:fontcolor=0xd8dee9,
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='REAL PUBLIC RECORD  #35':x=668:y=51:fontsize=17:fontcolor=0x7ee787,
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='$ node android-node-pick-regression.cjs':x=70:y=118:fontsize=21:fontcolor=0xa7b0c0:enable='between(t,0,3.5)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='FAIL  tap selected instance 71; expected 42':x=70:y=160:fontsize=24:fontcolor=0xff6b6b:enable='between(t,0.8,3.5)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='Agent\: searching shared debug memory before retrying...':x=70:y=118:fontsize=21:fontcolor=0x58d6ff:enable='between(t,3.5,8)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='$ noosphere-query "R3F mobile node tap selects wrong instance"':x=70:y=164:fontsize=19:fontcolor=0xd8dee9:enable='between(t,4.4,8)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='MATCH  VERIFIED SEED MEMORY  /  ISSUE #35':x=70:y=118:fontsize=23:fontcolor=0x7ee787:enable='between(t,8,14.2)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='ROOT CAUSE':x=70:y=166:fontsize=18:fontcolor=0xffd866:enable='between(t,8.6,14.2)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='Bloom footprint exceeded compact raycast geometry.':x=210:y=166:fontsize=18:fontcolor=0xd8dee9:enable='between(t,8.6,14.2)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='FIX':x=70:y=210:fontsize=18:fontcolor=0xffd866:enable='between(t,9.4,14.2)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='Sync an invisible hit layer; preserve instanceId;':x=126:y=210:fontsize=18:fontcolor=0xd8dee9:enable='between(t,9.4,14.2)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='rank candidates by screen-space touch intent.':x=126:y=242:fontsize=18:fontcolor=0xd8dee9:enable='between(t,9.4,14.2)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='SOURCE  github.com/JinNing6/Noosphere/issues/35':x=70:y=306:fontsize=17:fontcolor=0x8b949e:enable='between(t,10.4,14.2)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='$ node android-node-pick-regression.cjs':x=70:y=118:fontsize=21:fontcolor=0xa7b0c0:enable='between(t,14.2,18.7)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='PASS  intended instance 42 opened the detail panel':x=70:y=164:fontsize=24:fontcolor=0x7ee787:enable='between(t,15,18.7)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='One verified failure became reusable memory.':x=70:y=220:fontsize=20:fontcolor=0x58d6ff:enable='between(t,16,18.7)',
drawbox=x=42:y=414:w=876:h=92:color=0x111827:t=fill:enable='between(t,18.7,20)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='STOP SOLVING THE SAME BUG TWICE.':x=118:y=440:fontsize=31:fontcolor=0xffffff:enable='between(t,18.7,20)',
drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='14 live Skills  |  2 verified seeds  |  review-gated':x=70:y=532:fontsize=17:fontcolor=0x8b949e,
format=yuv420p[out]
'@

try {
    $singleLineFilter = $filter -replace "(`r`n|`n|`r)", ""
    [System.IO.File]::WriteAllText(
        $filterPath,
        $singleLineFilter,
        [System.Text.UTF8Encoding]::new($false)
    )
    & $Ffmpeg -y -f lavfi -i "color=c=0x07090f:s=960x570:d=20:r=12" -filter_complex_script $filterPath -map "[out]" -c:v libx264 -preset slow -crf 20 -movflags +faststart $mp4Path
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed while rendering MP4" }

    & $Ffmpeg -y -i $mp4Path -vf "fps=10,scale=960:-1:flags=lanczos,palettegen=max_colors=96:stats_mode=diff" $palettePath
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed while generating the GIF palette" }

    & $Ffmpeg -y -i $mp4Path -i $palettePath -lavfi "fps=10,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle" -loop 0 $gifPath
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed while rendering GIF" }
}
finally {
    Remove-Item -LiteralPath $filterPath -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $palettePath -Force -ErrorAction SilentlyContinue
}

Write-Output "Rendered $mp4Path"
Write-Output "Rendered $gifPath"
