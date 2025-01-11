### Portable Application Environment

This section contains information and files associated with creating a 'portable application environment' in MS Windows 
that has proven useful in the HSTL Metadata Project.

When an application is described as "portable," it means the software can run directly from a removable storage device like a USB drive without requiring installation on the host computer's operating system. Here are the key characteristics of a portable application:

1. No Installation Required
- The application can be run directly from its folder or thumb drive
- No files are installed into system directories
- No registry entries are created
- No system-wide changes are made to the computer

2. Storage and Mobility
- Can be stored on USB drives, external hard drives, or cloud storage
- Easily transferred between different computers
- Runs consistently across different Windows (or other) systems

3. Technical Characteristics
- Contains all necessary files within its own directory
- Does not modify system settings
- May make a temprary session change to path to enable desired CLI commands
- Saves user configurations and data within its own folder or a designated portable data directory
- Useful for users needing to:
  - Use software on multiple computers
  - Avoids leaving traces on shared or public computers
  - Maintains a consistent software configuration environment across devices

4. Advantages
- No administrative rights needed to run
- Faster to start and use
- Reduces system clutter
- Simplifies software management for a unique or specific task

5. Limitations
- May have reduced system functionality compared to installed versions
- Some advanced system features might be unavailable
- Performance can sometimes be slightly slower

Common sources for portable applications include PortableApps.com, alternative software sites, and some software developers who offer portable versions of their programs.
