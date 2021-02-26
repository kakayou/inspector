## disk
function get_disk()
{
    $disk = Get-WmiObject -Class win32_logicaldisk
    foreach ($Drivers in $disk)
    {
       $PartitionSize = "{0:N2}" -f ($Drivers.Size/1GB)
       $PartitionFreeSize = "{0:N2}" -f ($Drivers.FreeSpace/1GB)
       $PartitionID = $Drivers.DeviceID
       $disk_used_percent =  (($PartitionFreeSize/$PartitionSize)*100)
       "disk|{0}_size_free:{1}" -f $PartitionID,$PartitionFreeSize | Out-File -Append os_collect.tmp
       "disk|{0}_size_pfree:{1:N2}" -f $PartitionID,$disk_used_percent | Out-File -Append os_collect.tmp
    }
}

get_disk

# memery
function free_physics_ram()
{
$ops = Get-WmiObject -Class Win32_OperatingSystem
$free =([math]::round(($ops.FreePhysicalMemory / (1mb)), 2))
$total =([math]::round(($ops.TotalVisibleMemorySize / (1mb))))
$percent_mem = ($free/$total)*100
"mem|mem_free:{0}" -f $free | Out-File -Append os_collect.tmp
"mem|total:{0}" -f $total | Out-File -Append os_collect.tmp
"mem|mem_available_percent:{0:N2}" -f $percent_mem | Out-File -Append os_collect.tmp
}
free_physics_ram


#获取主机系统版本
function get_type()
{
   $os_type = Get-WmiObject -Class Win32_OperatingSystem | Select-Object -ExpandProperty Caption
   "machine|os:{0}" -f $os_type | Out-File -Append os_collect.tmp
}
get_type

# 获取CPU使用率
function get_cpu()
{
$cpu = Get-WmiObject -Class Win32_Processor
$logic_cores = @($cpu).count * $cpu.NumberOfLogicalProcessors
$cpu_percent = [math]::round($cpu.LoadPercentage*$logic_cores, 2)
"cpu|cores:$logic_cores" | Out-File -Append os_collect.tmp
"cpu|load15:{0}" -f $cpu_percent |  Out-File -Append os_collect.tmp
}
get_cpu



