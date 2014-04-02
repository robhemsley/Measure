package uk.co.robhemsley.utils;

public class Debug {
	
	public static String getClassName(){
		final Throwable t = new Throwable();
		final StackTraceElement methodCaller = t.getStackTrace()[1];
		
		return methodCaller.getClassName();
	}

}
