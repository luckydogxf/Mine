## Preface

故障实在太多，不能一一记录，这里只摘录了一部分而已。

## Methodology

Basically, trouble may raise because of the folloing reasons.

-  Human error. The common siuation are `incorrect misspelling` ,  `typos` in settings, `wrong crendentials`, `upper-lower-case-mixed`.etc. All could be boiled down
to carelessness of  human being, and the prevention  is `strict procedure` or `SOP`.
---  
- SElinux/AppArmor/security Group /Firewall restricted

常见的情况，folder的权限正常，但是某个程序访问还是提示 permission denied, 这是因为SElinux等会限制process对文件的访问。
在`public cloud`的环境下，可能会出现忘记设置`security group` 等导致的

---
- environment changes

  Note： 这个问题困扰了我很久。

  出故障的系统: 类似 Google docs一样的，实现在线文档功能，架构是： `Nginx + Nextcloud（PHP） + collabora`

  变化：  从ESXI VM搬迁到 `kubenetes` 环境下， 用户 无法和 之前一样 正常打开 office文档。

  解决过程：

    1. Nextcloud 可以连接到 collabora（render office文档的）, 访问记录在collabora 可以看到。
    2. 其他尝试耗费很多时间，用过 `tcpdump`等手段。
    3. Google chrome 发现， 浏览器访问 Nginx,然后被proxy到Nextcloud后，当用户访问office后，collabora似乎通过`websocket`，让浏览器直接和它建立了连接。
    4. 由于collabora在k8上，没有通过ingress 暴露服务，所以浏览器无法访问它，这样office访问就卡了，然后超时。
    5. 自己误以为collabora也是通过 Nginx 代理返给浏览器，就是因为这个错误的判断，导致了错误的方向。
    6. ESXI 上，collabora也是个Docker，由于可以直接访问VM以及对应端口，所以正常工作。

  解决办法： 通过 Ingress-Nginx发布collabora，让浏览器可以访问其服务，问题解决。
---

- Insufficient resources.

   案例： 某个系统CPU很高，8 vcpu，登录系统后，uptime发现 1分钟upload 是 21.

   解决过程： top 和 iostat 实时查看资源使用情况。

   OS的SWAP设置导致CPU 使用率很高， 因为kswapd是负责查看内存free page的daemon，它定期启动，然后检查free page的情况，如果
   不去，就会启动page回收，但SWAP太小的话，物理机内存无法被系统SWAP，导致page无法释放。kswapd就持续反复，非常占用CPU。

   扩大swap，然后重启即可，RHEL官方也有SWAP大小的建议

   其他资源不足导致的问题， 用户无法访问某个页面，登录到Nginx, 查看系统日志，出现 Too many open files。ulimit 发现系统用默认值1024，这个在连接数很多的时候，肯定是无法满足，直接扩大即可。

   与此同时，还需要关注 time_wait， backlog, net.core.somaxconn 这2个queue等。

    还遇到过其他同类的问题： Firewall的性能太差，经常出现cpu is 100%, 用户无法正常访问，只能替换掉。

---
- 设置不当导致的故障

于 IO scheduler 设置不当导致的用户使用体验不好。

某SAP 组件，用户读写比较平衡，并且运行在SAS Disk上，但是Linux的`io scheduler`却设为`mq-deadline` 导致用户写数据的时候，比较卡。

mq-deadline 是适用于读优先于写，读多写少的情况，

解决过程：
   查看`prometheus`监控，发现Disk的对比非常明显，由于mq-deadline给Read/Write 设了deadline,The default “deadline” values are 500 ms
   for Read operations and 5,000 ms for Write operations. 结果Rewrite明显比Write优先级高。当用户写的时候，就出现卡的情况。
   
   解决办法： 编辑/etc/grub/default, 添加
   ```
   GRUB_CMDLINE_LINUX="elevator=bfq"
   ```
   然后重新产生grub后重启即可，如果不能重启，直接 echo 到sys/block/sda/queue/scheduler 也可以。
   
   ---
   其他同类问题，系统大量进程，大内存，但是没有使用`huge page`, 导致CPU的`sys`使用率比较高。
   
---
-  MySQL Database有关的问题

   Slow query比较多，经过explain 发现，用户的SQL statement不正确，某个field的type是int, 但是SQL的where 后面却使用了''， 这样会导致index无效，直接做全表扫描。

   MySQL time wait的设置值太高，默认28800， 某个process完成后，一直处于sleep状态直到timeout，导致max connection被消耗完，然后新的连接失败。
   
   Database做升级后，创建database的时候，没有明确指定`character set`为`utf-8`, 那么就会使用默认的`latin-1`, 这样可能导致中文字符显示乱码等。

--- Unknown Bugs
   Dell 某个型号的服务器，intel 网卡驱动有Bug导致speed降级，用`ethtool`可以看到不正常，升级driver后解决问题。

## Tools
- Networking && connections: `tcpdump`
- system call: `strace`
- resources: `top`, 'vmstat`, 'iostat`. 
- Web: `Google chrome F12, debug`
- And so on

## Geneal guides

- Manpage, 
- log, 
- monitoring
- other approaches like googling, mailing list, github issue .etc.



